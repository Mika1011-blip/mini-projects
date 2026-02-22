
"""
Property Price Predictor (Tkinter)
----------------------------------
What this does
- Reads a CSV "model" with at least CAT, CENTROID, PRED (and ideally PRICE, AREA for heatmap).
- Drops NA rows.
- Builds UI with 2 dependent dropdowns: TYPE then LOC (both sourced from CAT tuples).
- Provides 8 numeric inputs for a POINT vector (area, terrain, neuf, dispo, etc. — you decide the mapping).
- Calls model_SL_predict(model=df, data={"CAT": (TYPE, LOC), "POINT": (x1,...,x8)}) to predict.
- Shows an optional heatmap (TYPE-switchable) with green (cheap) -> red (expensive).

How to run
  python property_price_app.py
(Requires: pandas, matplotlib; works on Python 3.9+; Tkinter is in the standard library.)

Notes
- We keep the provided model_SL_predict EXACTLY as given.
- We define get_shortestDistancePairs (needed by model_SL_predict).
- The CAT column should contain pairs like "('APPART A VENDR','75012')" or equivalent; we parse robustly.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog

import pandas as pd
import numpy as np
from ast import literal_eval
import math
from pathlib import Path

import os
import sys
import traceback

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button
from matplotlib import cm, colors

# ----------------------------
# Dependency for model_SL_predict
# ----------------------------
def get_shortestDistancePairs(classified_pts, unclassified_pts):
    """
    Return a dict mapping each point in unclassified_pts to the single nearest centroid in classified_pts.

    Parameters
    ----------
    classified_pts : Iterable of tuple/list of floats (centroids)
    unclassified_pts : Iterable of tuple/list of floats (query points)

    Returns
    -------
    dict: { unclassified_point_tuple : nearest_centroid_tuple }
    """
    # Convert to tuples of floats for hashability and numeric safety
    cents = [tuple(map(float, c)) for c in classified_pts if c is not None]
    out = {}
    for p in unclassified_pts:
        pt = tuple(map(float, p))
        best_c = None
        best_d = float('inf')
        for c in cents:
            # Euclidean distance
            if len(c) != len(pt):
                # dimension mismatch -> skip
                continue
            d = math.sqrt(sum((a-b)**2 for a,b in zip(pt, c)))
            if d < best_d:
                best_d = d
                best_c = c
        if best_c is None and cents:
            best_c = cents[0]
        out[pt] = best_c
    return out

# ----------------------------
# DO NOT MODIFY: Provided function
# ----------------------------
def model_SL_predict(csv_model : str = None, model : pd.core.frame.DataFrame = None ,data : dict = None ):
    """
    data : dict -> shape = {str:tuple,str:tuple} keys() = {"CAT","POINT"}
    out -> float
    """
    #safety check
    if model is None and not csv_model :
        raise ValueError("No model provided")
    if not data :
        return None
    if csv_model :
        try :
            model = pd.read_csv(csv_model)
        except Exception :
            raise ValueError("Error converting model_sl.csv to dataframe")
    model.dropna(inplace = True)
    #get model capability to predict (have predictable input category)
    if sorted(set(data.keys())) != sorted({"CAT","POINT"}):
        raise ValueError("Invalid data keys")
    predictable_cat = set(model["CAT"].tolist())
    if (data["CAT"] not in predictable_cat) or (len(data["CAT"]) != 2):
        raise ValueError("Incompatible category")
    if len(data["POINT"]) != 8 :
        raise ValueError("Incompatible point")
    mask = model["CAT"].apply(lambda x : sorted(x) == sorted(data["CAT"]) if x else False)
    centroids = set(model.loc[mask,"CENTROID"].tolist())
    pair = get_shortestDistancePairs(classified_pts=centroids,unclassified_pts=[data["POINT"]])
    key = tuple(map(float, data["POINT"]))
    nearest = pair[key]
    pred = set(model.loc[model["CENTROID"].isin([nearest]), "PRED"].tolist())
    return pred

# ----------------------------
# Helpers
# ----------------------------
def parse_cat_value(v):
    """Parse CAT cell into a (TYPE, LOC) tuple."""
    if pd.isna(v):
        return None
    if not isinstance(v, (list, tuple)):
        if isinstance(v, str):
            # try literal_eval
            try:
                v2 = literal_eval(v)
            except Exception:
                v2 = v
            v = v2
    if isinstance(v, (list, tuple, np.ndarray, pd.Series)):
        t = tuple(v)
    else:
        t = (v,)

    if len(t) == 0:
        return None
    type_part = str(t[0])
    loc_part  = str(t[1]) if len(t) > 1 else "UNKNOWN"
    return (type_part, loc_part)

def extract_type_loc_map(df):
    """
    From df['CAT'], build: types (sorted list), and mapping type->sorted list of locs.
    """
    cats = df["CAT"].apply(parse_cat_value).dropna()
    types = sorted(set([c[0] for c in cats]))
    by_type = {}
    for t in types:
        locs = sorted({c[1] for c in cats if c[0] == t})
        by_type[t] = locs
    return types, by_type

# ----------------------------
# Heatmap (TYPE-switchable), green->red (cheap->expensive)
# ----------------------------
def plot_type_loc_heatmap(df, rectangles_per_row: int = 6, figure_size=(13, 8)):
    """
    Render an interactive heatmap-of-rectangles by TYPE.
    Uses PRICE/AREA for €/m² if available; otherwise averages PRED/AREA if PRICE is missing.
    Colors: green (cheap) -> red (expensive) using 'RdYlGn_r'.
    """
    if "CAT" not in df.columns:
        raise ValueError("Dataframe missing 'CAT' column.")
    # parse CAT
    work = df.copy()
    work["CAT_TUP"] = work["CAT"].apply(parse_cat_value)
    work = work.dropna(subset=["CAT_TUP"])
    work["TYPE_"] = work["CAT_TUP"].apply(lambda t: t[0])
    work["LOC_"]  = work["CAT_TUP"].apply(lambda t: t[1])

    # Pick price per m²
    area = pd.to_numeric(work.get("AREA", np.nan), errors="coerce")
    price = pd.to_numeric(work.get("PRICE", np.nan), errors="coerce")
    pred  = pd.to_numeric(work.get("PRED", np.nan), errors="coerce")

    ppm2 = None
    if price.notna().any() and area.notna().any():
        ppm2 = price / area
    elif pred.notna().any() and area.notna().any():
        ppm2 = pred / area
    else:
        # fallback: just use PRED even if no AREA; not a €/m², but preserves ordering
        ppm2 = pred

    work["PPM2"] = pd.to_numeric(ppm2, errors="coerce")
    work = work.dropna(subset=["PPM2"])

    g = (
        work.groupby(["TYPE_", "LOC_"], dropna=False)["PPM2"]
            .mean()
            .reset_index()
    )

    types = g["TYPE_"].dropna().unique().tolist()
    if len(types) == 0:
        messagebox.showwarning("Heatmap", "No TYPE values found for heatmap.")
        return

    per_type = {}
    for t in types:
        sub = g[g["TYPE_"] == t].copy()
        sub = sub.sort_values("PPM2", ascending=False, kind="mergesort").reset_index(drop=True)
        per_type[t] = sub

    fig, ax = plt.subplots(figsize=figure_size)
    plt.subplots_adjust(bottom=0.22)
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_frame_on(False)

    cmap = plt.get_cmap("RdYlGn_r")  # green->red
    norm = colors.Normalize(vmin=0, vmax=1)
    sm = cm.ScalarMappable(norm=norm, cmap=cmap)

    rect_artists = []
    text_artists = []

    def draw_type(tname: str):
        for art in rect_artists:
            art.remove()
        rect_artists.clear()
        for txt in text_artists:
            txt.remove()
        text_artists.clear()

        sub = per_type[tname]
        n = len(sub)
        if n == 0:
            ax.set_title(f"{tname} (no LOC rows)")
            fig.canvas.draw_idle()
            return

        vmin, vmax = float(sub["PPM2"].min()), float(sub["PPM2"].max())
        if math.isclose(vmin, vmax):
            vmax = vmin + 1e-9
        sm.set_norm(colors.Normalize(vmin=vmin, vmax=vmax))

        cols = max(1, int(rectangles_per_row))
        rows = int(math.ceil(n / cols))
        pad = 0.04
        cell_w = 1.0 / cols
        cell_h = 1.0 / rows

        for idx, row in sub.iterrows():
            r = idx // cols
            c = idx % cols
            x0 = c * cell_w + pad * 0.5
            y0 = 1.0 - (r + 1) * cell_h + pad * 0.5
            w = cell_w - pad
            h = cell_h - pad
            val = float(row["PPM2"])
            color = sm.to_rgba(val)

            rect = Rectangle((x0, y0), w, h, linewidth=1.0, edgecolor="black", facecolor=color)
            ax.add_patch(rect)
            rect_artists.append(rect)

            label = f"{row['LOC_']}\n{val:,.0f}"
            txt = ax.text(x0 + w/2, y0 + h/2, label, ha="center", va="center", fontsize=9)
            text_artists.append(txt)

        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.set_title(f"TYPE: {tname} — Avg €/m² (or proxy) by LOC (n={n})")

        for im in ax.images:
            im.remove()
        legend_data = np.linspace(vmin, vmax, 256)[None, :]
        im = ax.imshow(legend_data, extent=(0.55, 0.95, -0.07, -0.03), aspect='auto',
                       origin='lower', cmap=cmap, norm=sm.norm)
        ax.text(0.55, -0.02, f"{vmin:,.0f}", ha="left", va="top", fontsize=8, transform=ax.transAxes)
        ax.text(0.95, -0.02, f"{vmax:,.0f}", ha="right", va="top", fontsize=8, transform=ax.transAxes)
        ax.text(0.75, -0.02, "€/m²", ha="center", va="top", fontsize=8, transform=ax.transAxes)

        fig.canvas.draw_idle()

    # Buttons per type at bottom
    btn_height = 0.05
    btn_width  = 0.12
    btn_pad_x  = 0.01
    btn_pad_y  = 0.01
    per_row = max(1, int((1.0 - 2*btn_pad_x) // (btn_width + btn_pad_x)))
    for i, t in enumerate(types):
        rowi = i // per_row
        coli = i % per_row
        left = 0.02 + coli * (btn_width + btn_pad_x)
        bottom = 0.02 + rowi * (btn_height + btn_pad_y)
        ax_btn = plt.axes([left, bottom, btn_width, btn_height])
        btn = Button(ax_btn, str(t))
        btn.on_clicked(lambda _evt, name=t: draw_type(name))

    draw_type(types[0])
    plt.show()

# ----------------------------
# Main App
# ----------------------------
class App(tk.Tk):
    def __init__(self, default_csv_path=None):
        super().__init__()
        self.title("Property Price Predictor")
        self.geometry("820x520")

        self.model_df = None
        self.type_to_locs = {}
        self.types = []

        # Layout weighting
        self.columnconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)

        self._build_toolbar()
        self._build_main()
        self._build_status()

        # Try to load default
        if default_csv_path and os.path.exists(default_csv_path):
            try:
                self.load_csv(default_csv_path)
            except Exception as e:
                messagebox.showwarning("Load CSV", f"Could not load default CSV:\n{e}")

    def _build_toolbar(self):
        bar = ttk.Frame(self, padding=8)
        bar.grid(row=0, column=0, sticky="ew")
        bar.columnconfigure(5, weight=1)

        ttk.Button(bar, text="Load CSV…", command=self.pick_csv).grid(row=0, column=0, padx=(0,8))

        ttk.Label(bar, text="TYPE").grid(row=0, column=1, padx=(0,6))
        self.type_var = tk.StringVar()
        self.type_cb = ttk.Combobox(bar, textvariable=self.type_var, state="readonly", width=28)
        self.type_cb.grid(row=0, column=2, padx=(0,12))
        self.type_cb.bind("<<ComboboxSelected>>", self.on_type_change)

        ttk.Label(bar, text="LOC").grid(row=0, column=3, padx=(0,6))
        self.loc_var = tk.StringVar()
        self.loc_cb = ttk.Combobox(bar, textvariable=self.loc_var, state="readonly", width=18)
        self.loc_cb.grid(row=0, column=4, padx=(0,12))

        ttk.Button(bar, text="Heatmap", command=self.show_heatmap).grid(row=0, column=6)

    def _build_main(self):
        body = ttk.Frame(self, padding=8)
        body.grid(row=1, column=0, sticky="nsew")
        body.columnconfigure(0, weight=1)
        body.rowconfigure(1, weight=1)

        # Inputs frame (8 numeric)
        inputs = ttk.LabelFrame(body, text="Point (8 values)", padding=8)
        inputs.grid(row=0, column=0, sticky="ew")
        for i in range(8):
            inputs.columnconfigure(i*2+1, weight=1)

        self.point_vars = [tk.StringVar() for _ in range(8)]
        labels = ["AREA","TERRAIN","NEUF","DISPO","CHAMBRE","PIECE","FLOOR","FLOORS"]
        for i, lab in enumerate(labels):
            ttk.Label(inputs, text=lab).grid(row=0, column=i*2, padx=(0,4))
            ttk.Entry(inputs, textvariable=self.point_vars[i], width=8).grid(row=0, column=i*2+1, padx=(0,10))

        # Table / preview pane
        table_frame = ttk.LabelFrame(body, text="Model preview (first 200 rows)", padding=8)
        table_frame.grid(row=1, column=0, sticky="nsew", pady=(8,0))
        table_frame.columnconfigure(0, weight=1); table_frame.rowconfigure(0, weight=1)

        self.tree = ttk.Treeview(table_frame, columns=("CAT","CENTROID","PRED"), show="headings", height=10)
        for col, w in [("CAT", 260), ("CENTROID", 360), ("PRED", 120)]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=w, anchor="w")
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")

        # Action row
        actions = ttk.Frame(body, padding=(0,8,0,0))
        actions.grid(row=2, column=0, sticky="ew")
        ttk.Button(actions, text="Predict", command=self.predict).grid(row=0, column=0)
        self.result_var = tk.StringVar(value="Prediction: —")
        ttk.Label(actions, textvariable=self.result_var, font=("TkDefaultFont", 10, "bold")).grid(row=0, column=1, padx=12)

    def _build_status(self):
        self.status_var = tk.StringVar(value="Load a CSV model to begin.")
        bar = ttk.Label(self, textvariable=self.status_var, anchor="w", padding=(8,3))
        bar.grid(row=2, column=0, sticky="ew")

    # ------------- Events / Actions -------------
    def pick_csv(self):
        path = filedialog.askopenfilename(
            title="Select model CSV",
            filetypes=[("CSV files","*.csv"), ("All files","*.*")]
        )
        if not path:
            return
        self.load_csv(path)

    def load_csv(self, path):
        df = pd.read_csv(path)
        # Drop NA rows
        df = df.dropna(how="any").copy()

        # Ensure required columns
        required_cols = {"CAT","CENTROID","PRED"}
        missing = required_cols - set(df.columns)
        if missing:
            raise ValueError(f"CSV is missing required columns: {missing}")

        # Normalize CAT and CENTROID types
        df["CAT"] = df["CAT"].apply(parse_cat_value)
        df["CENTROID"] = df["CENTROID"].apply(lambda v: tuple(map(float, literal_eval(v))) if isinstance(v, str) else tuple(v) if isinstance(v,(list,tuple)) else v)
        # Basic sanity: only keep rows with 2-cat and centroid length 8 if present
        df = df[df["CAT"].apply(lambda t: isinstance(t, tuple) and len(t)==2)]
        df = df[df["CENTROID"].apply(lambda c: isinstance(c, tuple) and len(c)>=1)]

        self.model_df = df.reset_index(drop=True)

        # Populate type/loc mapping
        self.types, self.type_to_locs = extract_type_loc_map(self.model_df)
        self.type_cb["values"] = self.types
        self.type_var.set(self.types[0] if self.types else "")
        self.update_locs()

        # Fill preview
        for i in self.tree.get_children():
            self.tree.delete(i)
        preview = self.model_df.head(200)
        for _, row in preview.iterrows():
            self.tree.insert("", "end", values=(row["CAT"], row["CENTROID"], row["PRED"]))

        self.status_var.set(f"Loaded: {os.path.basename(path)} | rows: {len(self.model_df)}")

    def on_type_change(self, _evt=None):
        self.update_locs()

    def update_locs(self):
        t = self.type_var.get()
        locs = self.type_to_locs.get(t, [])
        self.loc_cb["values"] = locs
        self.loc_var.set(locs[0] if locs else "")

    def predict(self):
        if self.model_df is None:
            messagebox.showwarning("Predict", "Please load a CSV model first.")
            return
        t = self.type_var.get().strip()
        l = self.loc_var.get().strip()
        if not t or not l:
            messagebox.showwarning("Predict", "Please select TYPE and LOC.")
            return

        # collect 8 numeric entries
        vals = []
        for i, var in enumerate(self.point_vars):
            s = var.get().strip()
            try:
                v = float(s)
            except Exception:
                messagebox.showerror("Invalid input", f"Value #{i+1} is not a number: {s!r}")
                return
            vals.append(v)
        if len(vals) != 8:
            messagebox.showerror("Invalid input", "Exactly 8 numeric values are required.")
            return

        data = {"CAT": (t, l), "POINT": tuple(vals)}
        try:
            pred = model_SL_predict(model=self.model_df, data=data)
        except Exception as e:
            messagebox.showerror("Prediction error", str(e))
            return

        if not pred:
            self.result_var.set("Prediction: (no result)")
        else:
            # pred is a set; display all values
            vals = sorted(list(pred))
            if len(vals) == 1:
                self.result_var.set(f"Prediction: {vals[0]:,.0f}")
            else:
                self.result_var.set(f"Prediction set: {', '.join(f'{v:,.0f}' for v in vals)}")

    def show_heatmap(self):
        if self.model_df is None:
            messagebox.showwarning("Heatmap", "Please load a CSV model first.")
            return
        try:
            plot_type_loc_heatmap(self.model_df, rectangles_per_row=6, figure_size=(13, 8))
        except Exception as e:
            messagebox.showerror("Heatmap error", str(e))



if __name__ == "__main__":
    # Optional default path via a small popup (text input)
    try:
        tmp_root = tk.Tk()
        tmp_root.withdraw()
        user_input = simpledialog.askstring("Open file", "Enter model filename (without or with .csv):", parent=tmp_root)
        tmp_root.destroy()
    except Exception as e:
        print("[Startup] Warning: could not show input dialog:", e)
        user_input = None

    default_path = None
    if user_input:
        p = user_input.strip()
        if p and not p.lower().endswith(".csv"):
            p += ".csv"
        candidate = Path(p)
        if not candidate.is_file():
            candidate2 = Path(__file__).with_name(p)
            if candidate2.is_file():
                candidate = candidate2
        if candidate.is_file():
            default_path = str(candidate)
        else:
            try:
                messagebox.showwarning("CSV not found", f"Could not find: {p}You can click 'Load CSV…' to choose a file.")
            except Exception as e:
                print("[Startup] CSV not found and cannot show messagebox:", e)

    try:
        app = App(default_csv_path=default_path)
        app.mainloop()
    except Exception as e:
        print("[Fatal] The app crashed on startup:")
        traceback.print_exc()
        try:
            # Try a last-chance dialog if Tk is available
            messagebox.showerror("Fatal error", f"The app crashed on startup:{e}")
        except Exception:
            pass
        sys.exit(1)
