# This cell defines a function that reads a CSV and renders an interactive, type-switchable
# "heatmap of rectangles" using matplotlib. Each rectangle represents a (TYPE, LOC) pair
# (taken from the `CAT` column), colored by the average price per m² computed from PRICE/AREA
# across all rows that share the same CAT (regardless of centroid). Buttons allow switching
# between TYPES. No explicit colormap is specified; matplotlib's default is used.
#
# After defining the function, we invoke it on the user's uploaded CSV (if present).

import pandas as pd
import numpy as np
import math
from ast import literal_eval

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.widgets import Button
from matplotlib import cm, colors

def plot_type_loc_heatmap(csv_file: str, rectangles_per_row: int = 6, figure_size=(12, 7)):
    """
    Render an interactive heatmap-of-rectangles by TYPE.
    
    Parameters
    ----------
    csv_file : str
        Path to CSV with columns: PRICE, AREA, CAT. CAT should encode (TYPE, LOC).
    rectangles_per_row : int, optional
        How many rectangles per row in the grid. Default 6.
    figure_size : tuple, optional
        Matplotlib figure size. Default (12, 7).
    """
    # ----- Load & basic prep -----
    df = pd.read_csv(csv_file)
    required = {"PRICE", "AREA", "CAT"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing required columns: {missing}")
    
    # robust CAT parsing -> tuple(TYPE, LOC)
    def parse_cat(v):
        if pd.isna(v):
            return None
        if isinstance(v, str):
            try:
                v2 = literal_eval(v)
            except Exception:
                v2 = v
            v = v2
        if isinstance(v, (list, tuple, np.ndarray, pd.Series)):
            t = tuple(v)
        else:
            t = (v,)
        # heuristic: expect (TYPE, LOC). If more than 2, take first two.
        if len(t) == 1:
            # ambiguous; treat as TYPE with unknown LOC
            return (str(t[0]), "UNKNOWN")
        type_part = str(t[0])
        loc_part = t[1] if len(t) > 1 else "UNKNOWN"
        return (type_part, loc_part)

    df = df.copy()
    df["CAT_TUP"] = df["CAT"].apply(parse_cat)
    df = df.dropna(subset=["CAT_TUP"])
    # split
    df["TYPE_"] = df["CAT_TUP"].apply(lambda t: t[0])
    df["LOC_"]  = df["CAT_TUP"].apply(lambda t: t[1])
    
    # numeric price per m2
    price = pd.to_numeric(df["PRICE"], errors="coerce")
    area  = pd.to_numeric(df["AREA"], errors="coerce")
    df["PPM2"] = price / area
    df = df.dropna(subset=["PPM2"])
    
    # group by exact CAT (TYPE, LOC), average PPM2
    g = (
        df.groupby(["TYPE_", "LOC_"], dropna=False)["PPM2"]
          .mean()
          .reset_index()
    )
    
    # collect types
    types = g["TYPE_"].dropna().unique().tolist()
    if len(types) == 0:
        raise ValueError("No TYPE values found after parsing CAT.")
    
    # precompute per-type dict for quick switching
    per_type = {}
    for t in types:
        sub = g[g["TYPE_"] == t].copy()
        # sort by value (optional for stable placement)
        sub = sub.sort_values("PPM2", ascending=False, kind="mergesort").reset_index(drop=True)
        per_type[t] = sub
    
    # ----- Build plotting canvas -----
    fig, ax = plt.subplots(figsize=figure_size)
    plt.subplots_adjust(bottom=0.22)  # leave room for buttons
    ax.set_xticks([]); ax.set_yticks([])
    ax.set_frame_on(False)
    
    # a single ScalarMappable we'll update per type; no explicit cmap to follow guidance
    default_cmap = cm.get_cmap()  # default colormap
    norm = colors.Normalize(vmin=0, vmax=1)
    sm = cm.ScalarMappable(norm=norm, cmap=default_cmap)
    
    rect_artists = []
    text_artists = []
    
    def draw_type(tname: str):
        # clear previous rectangles/texts
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
        
        # normalize colors per TYPE (relative expensiveness for this type)
        vmin, vmax = float(sub["PPM2"].min()), float(sub["PPM2"].max())
        # protect against flat distribution
        if math.isclose(vmin, vmax):
            vmax = vmin + 1e-9
        sm.set_norm(colors.Normalize(vmin=vmin, vmax=vmax))
        
        # layout
        cols = max(1, int(rectangles_per_row))
        rows = int(math.ceil(n / cols))
        # define grid in unit coords
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
            
            # label: LOC + value
            label = f"{row['LOC_']}\n{val:,.0f} €/m²"
            txt = ax.text(x0 + w/2, y0 + h/2, label, ha="center", va="center", fontsize=9)
            text_artists.append(txt)
        
        # title and colorbar-like legend using a side bar
        ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        ax.set_title(f"TYPE: {tname} — Avg price per m² by LOC\n(n={n})")
        
        # draw/update a small horizontal gradient bar at the bottom right as legend
        # We'll render a simple imshow as legend without specifying a colormap explicitly.
        # Remove previous legend imshow if present
        for im in ax.images:
            im.remove()
        # legend image
        legend_data = np.linspace(vmin, vmax, 256)[None, :]
        im = ax.imshow(legend_data, extent=(0.55, 0.95, -0.07, -0.03), aspect='auto', origin='lower', cmap=default_cmap, norm=sm.norm)
        ax.text(0.55, -0.02, f"{vmin:,.0f}", ha="left", va="top", fontsize=8, transform=ax.transAxes)
        ax.text(0.95, -0.02, f"{vmax:,.0f}", ha="right", va="top", fontsize=8, transform=ax.transAxes)
        ax.text(0.75, -0.02, "€/m²", ha="center", va="top", fontsize=8, transform=ax.transAxes)
        
        fig.canvas.draw_idle()
    
    # ----- Buttons -----
    # Create one button per TYPE, arranged in rows at the bottom
    btn_height = 0.05
    btn_width = 0.12
    btn_pad_x = 0.01
    btn_pad_y = 0.01
    per_row = max(1, int( (1.0 - 2*btn_pad_x) // (btn_width + btn_pad_x) ))
    btn_axes = []
    btn_objs = []
    
    for i, t in enumerate(types):
        rowi = i // per_row
        coli = i % per_row
        left = 0.02 + coli * (btn_width + btn_pad_x)
        bottom = 0.02 + rowi * (btn_height + btn_pad_y)
        ax_btn = plt.axes([left, bottom, btn_width, btn_height])
        btn = Button(ax_btn, str(t))
        btn_axes.append(ax_btn); btn_objs.append(btn)
        def _make_cb(name=t):
            return lambda event: draw_type(name)
        btn.on_clicked(_make_cb())
    
    # show first type by default
    draw_type(types[0])
    plt.show()


# Try to render the user's uploaded model if available
csv_path = "model_sl_10.csv"
import os
if os.path.exists(csv_path):
    plot_type_loc_heatmap(csv_path, rectangles_per_row=6, figure_size=(13, 8))
else:
    print("Upload a CSV and call: plot_type_loc_heatmap('/path/to/file.csv')")
