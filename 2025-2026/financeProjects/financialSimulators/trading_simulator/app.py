import random
import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(layout="wide")

import run_simulation_service as rs
import trade_service as trade

WINDOW_SIZE = 7
ENTRY_FEES_DEFAULT = 0.01
EXIT_FEES_DEFAULT = 0.05
DEFAULT_COUNTDOWN = 5


def _empty_orders():
    return pd.DataFrame(columns=[
        "order_id",
        "order_tickerSymbol",
        "order_created_at",
        "order_status",
        "order_side",
        "order_entry_price",
        "order_quantity",
        "order_sl",
        "order_tp",
    ])


def _empty_positions():
    return pd.DataFrame(columns=[
        "position_id",
        "position_order_id",
        "position_status",
        "position_tickerSymbol",
        "position_side",
        "position_quantity",
        "position_entry_price",
        "position_entry_at",
        "position_exit_at",
        "position_exit_price",
        "position_tp",
        "position_sl",
        "result_pnl_gross",
        "result_pnl_net",
        "result_entry_fees",
        "result_exit_fees",
    ])


def _init_simulation(ticker, period, start_mode, run_mode):
    data = rs.get_stockData(tickerSymbol=ticker, period=period)
    if isinstance(data, str):
        return data

    data = data.copy()
    data["Date"] = pd.to_datetime(data["Date"], errors="coerce")
    data = data.dropna(subset=["Date"]).sort_values("Date").reset_index(drop=True)
    if data.shape[0] < WINDOW_SIZE:
        return f"Not enough data to start. Need at least {WINDOW_SIZE} candles."

    if start_mode == "Random Start":
        start_idx = random.randint(0, data.shape[0] - WINDOW_SIZE)
    else:
        start_idx = 0

    idx = start_idx + WINDOW_SIZE - 1

    st.session_state["stockData"] = data
    st.session_state["tickerSymbol"] = ticker.strip().upper()
    st.session_state["mode"] = run_mode
    st.session_state["start_idx"] = start_idx
    st.session_state["idx"] = idx
    st.session_state["orders"] = _empty_orders()
    st.session_state["positions"] = _empty_positions()
    return None


def _update_after_step(entry_fees, exit_fees):
    data = st.session_state["stockData"]
    idx = st.session_state["idx"]
    if idx >= data.shape[0] - 1:
        return "Reached end of data."

    idx += 1
    st.session_state["idx"] = idx
    stock_slice = data.iloc[: idx + 1]

    resp = trade.update_data(
        orders=st.session_state["orders"],
        positions=st.session_state["positions"],
        stockData=stock_slice,
        entry_fees_percentage=entry_fees,
        exit_fees_percentage=exit_fees,
    )
    if not resp.get("success"):
        return resp.get("error_message")

    st.session_state["orders"] = resp.get("orders", st.session_state["orders"])
    st.session_state["positions"] = resp.get("positions", st.session_state["positions"])
    return None


def _countdown(seconds):
    if seconds <= 0:
        return
    bar = st.empty()
    text = st.empty()
    for remaining in range(seconds, 0, -1):
        progress = int(100 * (seconds - remaining) / seconds)
        if remaining <= max(1, seconds // 3):
            color = "#e74c3c"
        elif remaining <= max(1, 2 * seconds // 3):
            color = "#f39c12"
        else:
            color = "#2ecc71"
        bar.markdown(
            f"<div style='width:100%;background:#eee;border-radius:4px;height:10px;'>"
            f"<div style='width:{progress}%;background:{color};height:10px;border-radius:4px;'></div>"
            f"</div>",
            unsafe_allow_html=True,
        )
        text.markdown(f"Next candle in **{remaining}s**")
        time.sleep(1)
    bar.empty()
    text.empty()


st.write("# Trading simulator")

with st.form("setup_simulation_form"):
    ticker = st.text_input("Enter ticker symbol", value="GOOGL")
    period = st.selectbox("Data period", ["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)
    start_mode = st.radio("Initialization", ["From Beginning", "Random Start"])
    run_mode = st.radio("Run Mode", ["Automatic", "Manual"])
    submitted = st.form_submit_button("Start Simulation")

if submitted:
    err = _init_simulation(ticker, period, start_mode, run_mode)
    if err:
        st.error(err)

if "stockData" not in st.session_state:
    st.info("Enter a ticker and start the simulation.")
    st.stop()

# backward/partial state recovery
if "idx" not in st.session_state:
    st.session_state["idx"] = min(WINDOW_SIZE - 1, st.session_state["stockData"].shape[0] - 1)
if "start_idx" not in st.session_state:
    st.session_state["start_idx"] = max(0, st.session_state["idx"] - WINDOW_SIZE + 1)
if "orders" not in st.session_state:
    st.session_state["orders"] = _empty_orders()
if "positions" not in st.session_state:
    st.session_state["positions"] = _empty_positions()
if "tickerSymbol" not in st.session_state:
    st.session_state["tickerSymbol"] = str(ticker).strip().upper()
if "mode" not in st.session_state:
    st.session_state["mode"] = "Manual"
if "auto_running" not in st.session_state:
    st.session_state["auto_running"] = False

data = st.session_state["stockData"]
start_idx = st.session_state["start_idx"]
idx = st.session_state["idx"]
chart_data = data.iloc[start_idx: idx + 1]
current_row = data.iloc[idx]

entry_fees = st.sidebar.number_input("Entry fee (%)", min_value=0.0, max_value=1.0, value=ENTRY_FEES_DEFAULT, step=0.001)
exit_fees = st.sidebar.number_input("Exit fee (%)", min_value=0.0, max_value=1.0, value=EXIT_FEES_DEFAULT, step=0.001)
countdown_seconds = st.sidebar.number_input("Countdown (seconds)", min_value=0, value=DEFAULT_COUNTDOWN, step=1)

orders_df = st.session_state["orders"]
positions_df = st.session_state["positions"]

order_counts = orders_df["order_status"].value_counts() if "order_status" in orders_df.columns else pd.Series(dtype=int)
pending_orders = int(order_counts.get("PENDING", 0))
filled_orders = int(order_counts.get("FILLED", 0))

position_counts = positions_df["position_status"].value_counts() if "position_status" in positions_df.columns else pd.Series(dtype=int)
open_positions = int(position_counts.get("OPEN", 0))

gross_series = pd.to_numeric(positions_df.get("result_pnl_gross", pd.Series(dtype=float)), errors="coerce").fillna(0)
entry_fees_series = pd.to_numeric(positions_df.get("result_entry_fees", pd.Series(dtype=float)), errors="coerce").fillna(0)
exit_fees_series = pd.to_numeric(positions_df.get("result_exit_fees", pd.Series(dtype=float)), errors="coerce").fillna(0)
net_series = pd.to_numeric(positions_df.get("result_pnl_net", pd.Series(dtype=float)), errors="coerce")
net_series = net_series.fillna(gross_series - entry_fees_series - exit_fees_series)

total_pnl_gross = float(gross_series.sum())
total_pnl_net = float(net_series.sum())

left_col, right_col = st.columns([3, 2])

with left_col:
    st.subheader("Simulation Controls")
    if st.session_state["mode"] == "Automatic":
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("Start Auto"):
                st.session_state["auto_running"] = True
        with c2:
            if st.button("Stop Auto"):
                st.session_state["auto_running"] = False
        with c3:
            if st.button("Step Once"):
                _countdown(int(countdown_seconds))
                err = _update_after_step(entry_fees, exit_fees)
                if err:
                    st.warning(err)

        if st.session_state["auto_running"]:
            _countdown(int(countdown_seconds))
            err = _update_after_step(entry_fees, exit_fees)
            if err:
                st.warning(err)
                st.session_state["auto_running"] = False
            else:
                st.experimental_rerun()
    else:
        remaining = max(0, data.shape[0] - 1 - idx)
        step_count = st.number_input(
            "Advance steps",
            min_value=1,
            max_value=max(1, remaining),
            value=1,
            step=1,
            disabled=remaining == 0,
        )
        if st.button("Advance"):
            if remaining == 0:
                st.warning("Reached end of data.")
            else:
                steps = min(int(step_count), remaining)
                last_err = None
                for _ in range(steps):
                    last_err = _update_after_step(entry_fees, exit_fees)
                    if last_err:
                        break
                if last_err:
                    st.warning(last_err)

    if st.button("Reset Simulation"):
        st.session_state.clear()
        st.experimental_rerun()

    st.subheader("Statistics")
    gross_color = "#2ecc71" if total_pnl_gross >= 0 else "#e74c3c"
    net_color = "#2ecc71" if total_pnl_net >= 0 else "#e74c3c"
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(
            f"<div><div>PnL Gross</div>"
            f"<div style='color:{gross_color};font-size:22px;font-weight:600'>"
            f"{total_pnl_gross:.2f}</div></div>",
            unsafe_allow_html=True,
        )
    with s2:
        st.markdown(
            f"<div><div>PnL Net</div>"
            f"<div style='color:{net_color};font-size:22px;font-weight:600'>"
            f"{total_pnl_net:.2f}</div></div>",
            unsafe_allow_html=True,
        )
    s3.metric("Open Positions", int(open_positions))
    s4.metric("Pending Orders", pending_orders)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Date", str(current_row["Date"]))
    with c2:
        st.metric("Close", float(current_row["Close"]))
    with c3:
        st.metric("Open Positions", int(open_positions))

    fig = go.Figure(
        data=[
            go.Candlestick(
                x=chart_data["Date"].to_list(),
                low=chart_data["Low"].to_list(),
                open=chart_data["Open"].to_list(),
                high=chart_data["High"].to_list(),
                close=chart_data["Close"].to_list(),
                increasing_line_color="green",
                decreasing_line_color="red",
            )
        ]
    )
    fig.update_xaxes(type="date", autorange=True)
    fig.update_yaxes(type="linear", autorange=True)
    fig.update_layout(
        title=f"{st.session_state['tickerSymbol']} Chart",
        xaxis_title="Date",
        yaxis_title="Price",
        xaxis_rangeslider=dict(visible=True),
    )
    st.plotly_chart(fig, use_container_width=True)

with right_col:
    with st.expander("Place Order", expanded=True):
        side = st.selectbox("Side", ["BUY", "SELL"])
        quantity = st.number_input("Quantity", min_value=0.01, value=1.0, step=0.01)
        entry_price = st.number_input("Entry price", min_value=0.01, value=float(current_row["Close"]), step=0.01)
        use_tp = st.checkbox("Set TP")
        tp_price = st.number_input("TP price", min_value=0.01, value=float(current_row["Close"]), step=0.01, disabled=not use_tp)
        use_sl = st.checkbox("Set SL")
        sl_price = st.number_input("SL price", min_value=0.01, value=float(current_row["Close"]), step=0.01, disabled=not use_sl)

        if st.button("Place Order"):
            resp = trade.open_order(
                stockData=data.iloc[: idx + 1],
                order_tickerSymbol=st.session_state["tickerSymbol"],
                order_side=side,
                order_entry_price=entry_price,
                order_quantity=quantity,
                order_tp=tp_price if use_tp else None,
                order_sl=sl_price if use_sl else None,
                orders=st.session_state["orders"],
                positions=st.session_state["positions"],
                entry_fees_percentage=entry_fees,
            )
            if not resp.get("success"):
                st.error(resp.get("error_message"))
            else:
                st.session_state["orders"] = resp.get("orders", st.session_state["orders"])
                st.session_state["positions"] = resp.get("positions", st.session_state["positions"])

    st.subheader("Orders")
    st.dataframe(st.session_state["orders"], use_container_width=True)

    pending_orders = st.session_state["orders"]
    if "order_status" in pending_orders.columns:
        pending_orders = pending_orders[pending_orders["order_status"] == "PENDING"]
    if pending_orders.shape[0] > 0:
        st.markdown("**Pending Orders**")
        for _, row in pending_orders.iterrows():
            r1, r2, r3 = st.columns([3, 2, 2])
            with r1:
                st.write(row["order_id"])
            with r2:
                st.write(row["order_side"])
            with r3:
                if st.button("Cancel", key=f"cancel_{row['order_id']}"):
                    resp = trade.cancel_order(order_id=row["order_id"], orders=st.session_state["orders"])
                    if not resp.get("success"):
                        st.error(resp.get("error_message"))
                    else:
                        st.session_state["orders"] = resp.get("orders", st.session_state["orders"])

    st.subheader("Positions")
    st.dataframe(st.session_state["positions"], use_container_width=True)

    open_positions_df = st.session_state["positions"]
    if "position_status" in open_positions_df.columns:
        open_positions_df = open_positions_df[open_positions_df["position_status"] == "OPEN"]
    if open_positions_df.shape[0] > 0:
        st.markdown("**Open Positions**")
        for _, row in open_positions_df.iterrows():
            r1, r2, r3 = st.columns([3, 3, 2])
            with r1:
                st.write(row["position_id"])
            with r2:
                exit_price = st.number_input(
                    "Exit price",
                    min_value=0.01,
                    value=float(current_row["Close"]),
                    step=0.01,
                    key=f"exit_price_{row['position_id']}",
                )
            with r3:
                if st.button("Exit", key=f"exit_{row['position_id']}"):
                    resp = trade.exit_position(
                        position_id=row["position_id"],
                        positions=st.session_state["positions"],
                        stockData=data.iloc[: idx + 1],
                        exit_fees_percentage=exit_fees,
                        exit_price=exit_price,
                        exit_status="CLOSED_MANUAL",
                    )
                    if not resp.get("success"):
                        st.error(resp.get("error_message"))
                    else:
                        st.session_state["positions"] = resp.get("positions", st.session_state["positions"])
