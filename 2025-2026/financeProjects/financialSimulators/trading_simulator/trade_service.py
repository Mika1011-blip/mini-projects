import random
import pandas as pd
import uuid
from typing import Literal, Optional
import traceback


class order :
    def __init__(self,*,
                 order_id : str,
                 order_tickerSymbol : str,
                 order_created_at : pd.Timestamp,
                 order_side : Literal["BUY","SELL"],
                 order_entry_price : float,
                 order_quantity : float,
                 order_status : Literal["PENDING","FILLED","CANCELED"] = "PENDING",
                 order_sl : Optional[float] = None, #use mathematical approximation to close postion
                 order_tp : Optional[float] = None  #use mathematical approximation to close postion
                 ):
        #numeric sanity
        try :
            order_entry_price = float(order_entry_price)
        except :
            raise ValueError(f"Invalid order_entry_price : {order_entry_price}")
        try :
            order_quantity = float(order_quantity)
        except :
            raise ValueError(f"Invalid order_quantity : {order_quantity}")
        if order_sl is not None :
            try :
                order_sl = float(order_sl)
            except :
                raise ValueError(f"Invalid order_sl : {order_sl}")
        if order_tp is not None :
            try :
                order_tp = float(order_tp)
            except :
                raise ValueError(f"Invalid order_tp : {order_tp}")
        #timestamp sanity
        if not isinstance(order_created_at,pd.Timestamp):
            try :
                order_created_at = pd.Timestamp(order_created_at)
            except:
                raise ValueError(f"Invalid order_created_at : {order_created_at}")
        #type sanity
        if order_status not in ("PENDING","FILLED","CANCELED") :
            raise ValueError(f"Invalid order_status : {order_status}")
        if order_side not in ("BUY","SELL") :
            raise ValueError(f"Invalid order_side : {order_side}")
        #basic logic sanity
        if order_entry_price <= 0:
            raise ValueError(f"order_entry_price must be > 0 (input: {order_entry_price})")
        if order_quantity <= 0:
            raise ValueError(f"order_quantity must be > 0 (input: {order_quantity})")
        if order_side == "BUY":
            if order_sl is not None and order_sl >= order_entry_price:
                raise ValueError("For BUY, SL must be below entry price (sl < entry).")
            if order_tp is not None and order_tp <= order_entry_price:
                raise ValueError("For BUY, TP must be above entry price (entry < tp).")
        else:  # SELL
            if order_sl is not None and order_sl <= order_entry_price:
                raise ValueError("For SELL, SL must be above entry price (entry < sl).")
            if order_tp is not None and order_tp >= order_entry_price:
                raise ValueError("For SELL, TP must be below entry price (tp < entry).")
        #assign
        self.order_id = str(order_id)
        self.order_tickerSymbol = str(order_tickerSymbol)
        self.order_created_at = order_created_at
        self.order_status = order_status
        self.order_side = order_side
        self.order_entry_price = order_entry_price
        self.order_quantity = order_quantity
        self.order_sl = order_sl
        self.order_tp = order_tp
        
        #method
    def to_row(self):
        return {
            "order_id": self.order_id,
            "order_tickerSymbol": self.order_tickerSymbol,
            "order_created_at": self.order_created_at,
            "order_status": self.order_status,
            "order_side": self.order_side,
            "order_entry_price": self.order_entry_price,
            "order_quantity": self.order_quantity,
            "order_sl": self.order_sl,
            "order_tp": self.order_tp,
        }


class position :
    def __init__(self,*,
                 position_id : str,
                 position_order_id : str,
                 position_tickerSymbol : str,
                 position_side : Literal["LONG","SHORT"],
                 position_quantity : float,
                 position_entry_price : float,
                 position_entry_at : pd.Timestamp,
                 result_pnl_gross : float,
                 position_status : Literal["OPEN","CLOSED_TP","CLOSED_SL","CLOSED_MANUAL"] = "OPEN",
                 position_exit_price : Optional[float] = None,
                 position_exit_at : Optional[pd.Timestamp] = None,
                 position_tp : Optional[float] = None,
                 position_sl : Optional[float] = None,
                 result_pnl_net : Optional[float] = None,
                 result_entry_fees : Optional[float] = None,
                 result_exit_fees : Optional[float] = None     
                 ):
        #type sanity
        if position_status not in ("OPEN","CLOSED_TP","CLOSED_SL","CLOSED_MANUAL"):
            raise ValueError(f"Invalid position_status : {position_status}")
        if position_side not in ("LONG","SHORT") :
            raise ValueError(f"Invalid position_side : {position_side}")
        if not isinstance(position_entry_at, pd.Timestamp):
            try :
                position_entry_at = pd.Timestamp(position_entry_at)
            except :
                raise TypeError(f"position_entry_at must be a pandas Timestamp (got {type(position_entry_at)})")
        if position_exit_at is not None and not isinstance(position_exit_at, pd.Timestamp):
            try :
                position_exit_at = pd.Timestamp(position_exit_at)
            except:
                raise TypeError("position_exit_at must be a pandas Timestamp or None")
        #numeric sanity (coerce)
        try:
            position_quantity = float(position_quantity)
        except Exception:
            raise ValueError(f"Invalid position_quantity: {position_quantity}")

        try:
            position_entry_price = float(position_entry_price)
        except Exception:
            raise ValueError(f"Invalid position_entry_price: {position_entry_price}")

        if position_tp is not None:
            try:
                position_tp = float(position_tp)
            except Exception:
                raise ValueError(f"Invalid position_tp: {position_tp}")

        if position_sl is not None:
            try:
                position_sl = float(position_sl)
            except Exception:
                raise ValueError(f"Invalid position_sl: {position_sl}")

        if position_exit_price is not None:
            try:
                position_exit_price = float(position_exit_price)
            except Exception:
                raise ValueError(f"Invalid position_exit_price: {position_exit_price}")
        try:
            result_pnl_gross = float(result_pnl_gross)
        except Exception:
            raise ValueError(f"Invalid result_pnl_gross: {result_pnl_gross}")

        if result_pnl_net is not None:
            try:
                result_pnl_net = float(result_pnl_net)
            except Exception:
                raise ValueError(f"Invalid result_pnl_net: {result_pnl_net}")

        if result_entry_fees is not None:
            try:
                result_entry_fees = float(result_entry_fees)
            except Exception:
                raise ValueError(f"Invalid result_entry_fees: {result_entry_fees}")

        if result_exit_fees is not None:
            try:
                result_exit_fees = float(result_exit_fees)
            except Exception:
                raise ValueError(f"Invalid result_exit_fees: {result_exit_fees}")
        #numeric logic sanity
        if position_quantity <= 0:
            raise ValueError(f"position_quantity must be > 0 (input: {position_quantity})")
        if position_entry_price <= 0:
            raise ValueError(f"position_entry_price must be > 0 (input: {position_entry_price})")

        if position_tp is not None and position_tp <= 0:
            raise ValueError(f"position_tp must be > 0 (input: {position_tp})")
        if position_sl is not None and position_sl <= 0:
            raise ValueError(f"position_sl must be > 0 (input: {position_sl})")
        #TP/SL direction sanity
        if position_tp is not None and position_sl is not None:
            if position_side == "LONG":
                if position_sl >= position_entry_price:
                    raise ValueError("For LONG, SL must be below entry price (sl < entry).")
                if position_tp <= position_entry_price:
                    raise ValueError("For LONG, TP must be above entry price (entry < tp).")
            else:  # SHORT
                if position_sl <= position_entry_price:
                    raise ValueError("For SHORT, SL must be above entry price (entry < sl).")
                if position_tp >= position_entry_price:
                    raise ValueError("For SHORT, TP must be below entry price (tp < entry).")
        #time sanity
        if position_exit_at is not None and position_exit_at < position_entry_at:
            raise ValueError("position_exit_at cannot be earlier than position_entry_at")
        #closed/open consistency
        is_closed = position_status != "OPEN"
        if is_closed:
            if position_exit_at is None:
                raise ValueError("Closed position must have position_exit_at")
            if position_exit_price is None:
                raise ValueError("Closed position must have position_exit_price")
        else:
            # OPEN position should not have exit fields/results yet (keep it strict to avoid weird states)
            if position_exit_at is not None or position_exit_price is not None:
                raise ValueError("OPEN position cannot have exit_at/exit_price set")
        #assign attributes
        self.position_id = str(position_id)
        self.position_order_id = str(position_order_id)
        self.position_status = position_status
        self.position_tickerSymbol = str(position_tickerSymbol)
        self.position_side = position_side
        self.position_quantity = float(position_quantity)
        self.position_entry_price = float(position_entry_price)
        self.position_entry_at = position_entry_at

        self.position_exit_at = position_exit_at
        self.position_exit_price = position_exit_price

        self.position_tp = position_tp
        self.position_sl = position_sl

        self.result_pnl_gross = result_pnl_gross
        self.result_pnl_net = result_pnl_net
        self.result_entry_fees = result_entry_fees
        self.result_exit_fees = result_exit_fees

    #method
    def to_row(self):
        return {
            "position_id": self.position_id,
            "position_order_id": self.position_order_id,
            "position_status": self.position_status,
            "position_tickerSymbol": self.position_tickerSymbol,
            "position_side": self.position_side,
            "position_quantity": self.position_quantity,
            "position_entry_price": self.position_entry_price,
            "position_entry_at": self.position_entry_at,
            "position_exit_at": self.position_exit_at,
            "position_exit_price": self.position_exit_price,
            "position_tp": self.position_tp,
            "position_sl": self.position_sl,
            "result_pnl_gross": self.result_pnl_gross,
            "result_pnl_net": self.result_pnl_net,
            "result_entry_fees": self.result_entry_fees,
            "result_exit_fees": self.result_exit_fees,
        }
def open_order(*,
        stockData : pd.DataFrame,
        order_tickerSymbol : str,
        order_side : Literal["BUY","SELL"],
        order_entry_price : float,
        order_quantity : float,
        order_status : Literal["PENDING","FILLED","CANCELED"] = "PENDING",
        order_sl : Optional[float] = None,
        order_tp : Optional[float] = None,
        orders : Optional[pd.DataFrame] = None,
        positions : Optional[pd.DataFrame] = None,
        entry_fees_percentage : float = 0.01,
):
    out_positions = positions
    try :
        #pd.Dataframe sanity
        if not isinstance(stockData,pd.DataFrame):
            raise ValueError(f"Invalid stockData : {stockData}")
        if not isinstance(orders, pd.DataFrame) and orders is not None:
            raise ValueError(f"Invalid orders : {orders}")
        if not isinstance(positions, pd.DataFrame) and positions is not None:
            raise ValueError(f"Invalid positions : {positions}")
        #verify stockdata content:
        if stockData.shape[0] <= 0 :
            raise ValueError(f"No content in stockData : {stockData}")
        #stockData columns sanity
        required = {"Open", "High", "Low", "Close", "Date"}
        if not required.issubset(stockData.columns):
            missing = required - set(stockData.columns)
            raise ValueError(f"Missing columns: {missing}")
        #adjust entry price if necessary
        order_created_at = stockData["Date"].iloc[-1]
        try :
            market_price = float(stockData["Close"].iloc[-1])
        except :
            raise ValueError(f"Can't extract market price from col 'Close' in stockData : {stockData.iloc[-1]}")
        try:
            order_entry_price = float(order_entry_price)
        except Exception:
            raise ValueError(f"Invalid order_entry_price : {order_entry_price}")
        if order_side == "BUY" :
            order_entry_price = min([market_price,order_entry_price])
        elif order_side == "SELL" :
            order_entry_price = max([market_price,order_entry_price])
        #create order
        order_id = "ORDER" + str(uuid.uuid4())
        orderObj = order(
            order_id=order_id,
            order_tickerSymbol=order_tickerSymbol,
            order_created_at=order_created_at,
            order_status=order_status,
            order_side=order_side,
            order_entry_price=order_entry_price,
            order_quantity=order_quantity,
            order_sl=order_sl,
            order_tp=order_tp
        )
        order_df = pd.DataFrame([
                orderObj.to_row()
            ])
        out_orders = order_df if orders is None else  pd.concat([orders, order_df])

        if order_df["order_entry_price"].iloc[0] == market_price :
            response = exec_order(
                order_id=order_id,
                orders=out_orders,
                entry_fees_percentage=entry_fees_percentage,
                stockData=stockData,
                positions=out_positions,
            )
            if not response.get("success"):
                raise ValueError(response.get("error_message"))
            out_orders = response.get("orders", out_orders)
            out_positions = response.get("positions", out_positions)
        if out_positions is None:
            out_positions = pd.DataFrame(columns=[
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
        return {"orders" : out_orders,
                "positions" : out_positions,
                "success" : True }
    except Exception as e:
        return {
            "orders" : orders,
            "positions" : out_positions,
            "success" : False,
            "error_message" : str(e),
            "error_type": type(e).__name__,
            "error_trace": traceback.format_exc(),
        }
def cancel_order(*,
                 order_id : str,
                 orders : pd.DataFrame,
                 ):
    out = orders
    try :
        if not isinstance(orders,pd.DataFrame):
            raise ValueError(f"Invalid orders : {orders}")
        if "order_id" not in orders.columns or "order_status" not in orders.columns:
            raise ValueError(f"orders must include order_id and order_status columns")
        out = orders.copy()
        mask = out["order_id"].astype(str) == str(order_id)
        matched = out[mask].copy()
        if matched.shape[0] != 1 :
            raise ValueError(f"No Id matched or duplicated Id : {matched}")
        if matched["order_status"].iloc[0] != "PENDING" :
            raise ValueError(f"Order is either canceled or filled : {matched}")
        out.loc[mask, "order_status"] = "CANCELED"
        return{
            "orders" : out,
            "success" : True,
        }
    except Exception as e:
        return {
            "orders" : out,
            "success" : False,
            "error_message" : str(e),
            "error_type": type(e).__name__,
            "error_trace": traceback.format_exc(),
        }
    

def exec_order(
        order_id : str,
        orders : pd.DataFrame,
        entry_fees_percentage : float,
        stockData : pd.DataFrame,
        positions : Optional[pd.DataFrame] = None,
):
    out_orders = orders
    out_positions = positions
    try :
        #sanity
        if not isinstance(stockData,pd.DataFrame):
            raise ValueError(f"Invalid stockData : {stockData}")
        if not isinstance(orders, pd.DataFrame):
            raise ValueError(f"Invalid orders : {orders}")
        if orders.shape[0] == 0:
            raise ValueError("No orders in orders DataFrame")
        required_cols = {
            "order_id",
            "order_status",
            "order_side",
            "order_entry_price",
            "order_quantity",
            "order_tickerSymbol",
            "order_created_at",
        }
        missing = required_cols - set(orders.columns)
        if missing:
            raise ValueError(f"Missing order columns: {missing}")

        if positions is not None and not isinstance(positions, pd.DataFrame):
            raise ValueError(f"Invalid positions : {positions}")

        try:
            entry_fees_percentage = float(entry_fees_percentage)
        except Exception:
            raise ValueError(f"Invalid entry_fees_percentage : {entry_fees_percentage}")
        if entry_fees_percentage < 0:
            raise ValueError("entry_fees_percentage must be >= 0")

        mask = orders["order_id"].astype(str) == str(order_id)
        matched = orders[mask]
        if matched.shape[0] != 1:
            raise ValueError(f"No Id matched or duplicated Id : {matched}")
        if matched["order_status"].iloc[0] != "PENDING":
            raise ValueError(f"Order is either canceled or filled : {matched}")
        #verify stockdata content:
        if stockData.shape[0] <= 0 :
            raise ValueError(f"No content in stockData : {stockData}")
        #stockData columns sanity
        required = {"Open", "High", "Low", "Close", "Date"}
        if not required.issubset(stockData.columns):
            missing = required - set(stockData.columns)
            raise ValueError(f"Missing columns: {missing}")
        #logic
        out_orders.loc[mask,"order_status"] = "FILLED"
        position_id = "POSITION" + str(uuid.uuid4())
        position_tickerSymbol = out_orders.loc[mask,"order_tickerSymbol"].iloc[0]
        position_side = "LONG" if out_orders.loc[mask,"order_side"].iloc[0] == "BUY" else "SHORT"
        position_entry_price = out_orders.loc[mask,"order_entry_price"].iloc[0]
        position_entry_at = stockData["Date"].iloc[-1]
        position_quantity = out_orders.loc[mask,"order_quantity"].iloc[0]
        #compute
        position_amount =  position_quantity * position_entry_price
        result_entry_fees = entry_fees_percentage * position_amount

        current_price = float(stockData["Close"].iloc[-1])
        if position_side == "LONG" :
            result_pnl_gross = (current_price - position_entry_price) * position_quantity
        else :
            result_pnl_gross = (position_entry_price - current_price) * position_quantity
        #construct position object
        positionObj = position(
            position_id=position_id,
            position_order_id=order_id,
            position_tickerSymbol=position_tickerSymbol,
            position_side=position_side,
            position_entry_at=position_entry_at,
            position_entry_price=position_entry_price,
            position_quantity=position_quantity,
            result_entry_fees=result_entry_fees,
            position_tp=out_orders.loc[mask, "order_tp"].iloc[0],
            position_sl=out_orders.loc[mask, "order_sl"].iloc[0],
            result_pnl_gross=result_pnl_gross,
        )
        position_df = pd.DataFrame([positionObj.to_row()])
        if out_positions is None:
            return {
                "orders": out_orders,
                "positions": position_df,
                "success": True,
            }
        else:
            return {
                "orders": out_orders,
                "positions": pd.concat([out_positions, position_df], ignore_index=True),
                "success": True,
            }
    except Exception as e:
        return {
            "orders" : out_orders,
            "positions" : out_positions,
            "success" : False,
            "error_message" : str(e),
            "error_type": type(e).__name__,
            "error_trace": traceback.format_exc(),
        }

def set_tp(*,
           order_id : str,
           order_tp : float,
           orders : pd.DataFrame,
           positions : Optional[pd.DataFrame] = None,
           ):
    out_orders = orders
    out_positions = positions
    try :
        if not isinstance(orders,pd.DataFrame):
            raise ValueError(f"Invalid orders : {orders}")
        if orders.shape[0] == 0:
            raise ValueError("No orders in orders DataFrame")
        if positions is not None and not isinstance(positions,pd.DataFrame):
            raise ValueError(f"Invalid positions : {positions}")
        try:
            order_tp = float(order_tp)
        except Exception:
            raise ValueError(f"Invalid order_tp : {order_tp}")
        if order_tp <= 0:
            raise ValueError("order_tp must be > 0")

        required_order_cols = {
            "order_id",
            "order_status",
            "order_side",
            "order_entry_price",
            "order_quantity",
            "order_tickerSymbol",
            "order_created_at",
            "order_tp",
        }
        missing = required_order_cols - set(orders.columns)
        if missing:
            raise ValueError(f"Missing order columns: {missing}")

        mask = orders["order_id"].astype(str) == str(order_id)
        matched = orders[mask]
        if matched.shape[0] != 1:
            raise ValueError(f"No Id matched or duplicated Id : {matched}")

        order_status = matched["order_status"].iloc[0]
        order_side = matched["order_side"].iloc[0]
        order_entry_price = float(matched["order_entry_price"].iloc[0])

        if order_side == "BUY":
            if order_tp <= order_entry_price:
                raise ValueError("For BUY, TP must be above entry price (entry < tp).")
        else:
            if order_tp >= order_entry_price:
                raise ValueError("For SELL, TP must be below entry price (tp < entry).")

        out_orders = orders.copy()
        out_orders.loc[mask, "order_tp"] = order_tp

        if order_status == "FILLED":
            if positions is None:
                raise ValueError("positions is required when setting TP for a filled order")
            required_position_cols = {
                "position_order_id",
                "position_side",
                "position_status",
                "position_tp",
            }
            missing = required_position_cols - set(positions.columns)
            if missing:
                raise ValueError(f"Missing position columns: {missing}")

            pos_mask = (
                (positions["position_order_id"].astype(str) == str(order_id)) &
                (positions["position_status"] == "OPEN")
            )
            pos_matched = positions[pos_mask]
            if pos_matched.shape[0] != 1:
                raise ValueError(f"No position matched or duplicated position : {pos_matched}")

            out_positions = positions.copy()
            out_positions.loc[pos_mask, "position_tp"] = order_tp
        elif order_status == "CANCELED":
            raise ValueError("Cannot set TP on a canceled order")

        return{
            "orders" : out_orders,
            "positions" : out_positions,
            "success" : True,
        }
    except Exception as e:
        return {
            "orders" : out_orders,
            "positions" : out_positions,
            "success" : False,
            "error_message" : str(e),
            "error_type": type(e).__name__,
            "error_trace": traceback.format_exc(),
        }

def set_sl(*,
           order_id : str,
           order_sl : float,
           orders : pd.DataFrame,
           positions : Optional[pd.DataFrame] = None,
           ):
    out_orders = orders
    out_positions = positions
    try :
        if not isinstance(orders,pd.DataFrame):
            raise ValueError(f"Invalid orders : {orders}")
        if orders.shape[0] == 0:
            raise ValueError("No orders in orders DataFrame")
        if positions is not None and not isinstance(positions,pd.DataFrame):
            raise ValueError(f"Invalid positions : {positions}")
        try:
            order_sl = float(order_sl)
        except Exception:
            raise ValueError(f"Invalid order_sl : {order_sl}")
        if order_sl <= 0:
            raise ValueError("order_sl must be > 0")

        required_order_cols = {
            "order_id",
            "order_status",
            "order_side",
            "order_entry_price",
            "order_quantity",
            "order_tickerSymbol",
            "order_created_at",
            "order_sl",
        }
        missing = required_order_cols - set(orders.columns)
        if missing:
            raise ValueError(f"Missing order columns: {missing}")

        mask = orders["order_id"].astype(str) == str(order_id)
        matched = orders[mask]
        if matched.shape[0] != 1:
            raise ValueError(f"No Id matched or duplicated Id : {matched}")

        order_status = matched["order_status"].iloc[0]
        order_side = matched["order_side"].iloc[0]
        order_entry_price = float(matched["order_entry_price"].iloc[0])

        if order_side == "BUY":
            if order_sl >= order_entry_price:
                raise ValueError("For BUY, SL must be below entry price (sl < entry).")
        else:
            if order_sl <= order_entry_price:
                raise ValueError("For SELL, SL must be above entry price (entry < sl).")

        out_orders = orders.copy()
        out_orders.loc[mask, "order_sl"] = order_sl

        if order_status == "FILLED":
            if positions is None:
                raise ValueError("positions is required when setting SL for a filled order")
            required_position_cols = {
                "position_order_id",
                "position_side",
                "position_status",
                "position_sl",
            }
            missing = required_position_cols - set(positions.columns)
            if missing:
                raise ValueError(f"Missing position columns: {missing}")

            pos_mask = (
                (positions["position_order_id"].astype(str) == str(order_id)) &
                (positions["position_status"] == "OPEN")
            )
            pos_matched = positions[pos_mask]
            if pos_matched.shape[0] != 1:
                raise ValueError(f"No position matched or duplicated position : {pos_matched}")

            out_positions = positions.copy()
            out_positions.loc[pos_mask, "position_sl"] = order_sl
        elif order_status == "CANCELED":
            raise ValueError("Cannot set SL on a canceled order")

        return{
            "orders" : out_orders,
            "positions" : out_positions,
            "success" : True,
        }
    except Exception as e:
        return {
            "orders" : out_orders,
            "positions" : out_positions,
            "success" : False,
            "error_message" : str(e),
            "error_type": type(e).__name__,
            "error_trace": traceback.format_exc(),
        }

def exit_position(*,
        position_id : str,
        positions : pd.DataFrame,
        stockData : pd.DataFrame,
        exit_fees_percentage : float = 0.0,
        exit_price : Optional[float] = None,
        exit_status : Literal["CLOSED_TP","CLOSED_SL","CLOSED_MANUAL"] = "CLOSED_MANUAL",
):
    out_positions = positions
    try :
        if not isinstance(positions, pd.DataFrame):
            raise ValueError(f"Invalid positions : {positions}")
        if positions.shape[0] == 0:
            raise ValueError("No positions in positions DataFrame")

        if not isinstance(stockData,pd.DataFrame):
            raise ValueError(f"Invalid stockData : {stockData}")
        if stockData.shape[0] <= 0 :
            raise ValueError(f"No content in stockData : {stockData}")
        required = {"Close", "Date"}
        if not required.issubset(stockData.columns):
            missing = required - set(stockData.columns)
            raise ValueError(f"Missing columns: {missing}")

        try:
            exit_fees_percentage = float(exit_fees_percentage)
        except Exception:
            raise ValueError(f"Invalid exit_fees_percentage : {exit_fees_percentage}")
        if exit_fees_percentage < 0:
            raise ValueError("exit_fees_percentage must be >= 0")

        if exit_status not in ("CLOSED_TP","CLOSED_SL","CLOSED_MANUAL"):
            raise ValueError(f"Invalid exit_status : {exit_status}")

        required_position_cols = {
            "position_id",
            "position_status",
            "position_side",
            "position_entry_price",
            "position_entry_at",
            "position_quantity",
        }
        missing = required_position_cols - set(positions.columns)
        if missing:
            raise ValueError(f"Missing position columns: {missing}")

        mask = positions["position_id"].astype(str) == str(position_id)
        matched = positions[mask]
        if matched.shape[0] != 1:
            raise ValueError(f"No Id matched or duplicated Id : {matched}")
        if matched["position_status"].iloc[0] != "OPEN":
            raise ValueError(f"Position is not OPEN : {matched}")

        if exit_price is None:
            exit_price = float(stockData["Close"].iloc[-1])
        else:
            try:
                exit_price = float(exit_price)
            except Exception:
                raise ValueError(f"Invalid exit_price : {exit_price}")
        if exit_price <= 0:
            raise ValueError("exit_price must be > 0")

        exit_at = stockData["Date"].iloc[-1]
        entry_at = matched["position_entry_at"].iloc[0]
        if not isinstance(exit_at, pd.Timestamp):
            try:
                exit_at = pd.Timestamp(exit_at)
            except Exception:
                raise ValueError(f"Invalid exit_at : {exit_at}")
        if exit_at < entry_at:
            raise ValueError("exit_at cannot be earlier than position_entry_at")

        position_side = matched["position_side"].iloc[0]
        entry_price = float(matched["position_entry_price"].iloc[0])
        quantity = float(matched["position_quantity"].iloc[0])

        if position_side == "LONG":
            result_pnl_gross = (exit_price - entry_price) * quantity
        else:
            result_pnl_gross = (entry_price - exit_price) * quantity

        entry_fees = 0.0
        if "result_entry_fees" in positions.columns:
            val = matched["result_entry_fees"].iloc[0]
            if val is not None and not pd.isna(val):
                entry_fees = float(val)

        result_exit_fees = exit_fees_percentage * (exit_price * quantity)
        result_pnl_net = result_pnl_gross - entry_fees - result_exit_fees

        out_positions = positions.copy()
        out_positions.loc[mask, "position_exit_price"] = exit_price
        out_positions.loc[mask, "position_exit_at"] = exit_at
        out_positions.loc[mask, "position_status"] = exit_status
        out_positions.loc[mask, "result_pnl_gross"] = result_pnl_gross
        out_positions.loc[mask, "result_exit_fees"] = result_exit_fees
        out_positions.loc[mask, "result_pnl_net"] = result_pnl_net

        return{
            "positions" : out_positions,
            "success" : True,
        }
    except Exception as e:
        return {
            "positions" : out_positions,
            "success" : False,
            "error_message" : str(e),
            "error_type": type(e).__name__,
            "error_trace": traceback.format_exc(),
        }
    

def update_data(orders : pd.DataFrame,
                positions : pd.DataFrame,
                stockData : pd.DataFrame,
                entry_fees_percentage : float = 0.01,
                exit_fees_percentage : float = 0.05,
                ):
    out_orders = orders
    out_positions = positions
    try :
        #sanity
        if not isinstance(orders, pd.DataFrame):
            raise ValueError(f"Invalid orders : {orders}")
        if not isinstance(positions, pd.DataFrame):
            raise ValueError(f"Invalid positions : {positions}")
        if not isinstance(stockData, pd.DataFrame):
            raise ValueError(f"Invalid stockData : {stockData}")

        required_order_cols = {
            "order_id",
            "order_status",
            "order_side",
            "order_entry_price",
            "order_quantity",
            "order_tickerSymbol",
            "order_created_at",
            "order_sl",
            "order_tp",
        }
        missing = required_order_cols - set(orders.columns)
        if missing:
            raise ValueError(f"Missing order columns: {missing}")

        required_position_cols = {
            "position_id",
            "position_order_id",
            "position_status",
            "position_side",
            "position_entry_price",
            "position_entry_at",
            "position_quantity",
            "position_tp",
            "position_sl",
        }
        missing = required_position_cols - set(positions.columns)
        if missing:
            raise ValueError(f"Missing position columns: {missing}")

        required_stock_cols = {"Open", "High", "Low", "Close", "Date"}
        missing = required_stock_cols - set(stockData.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        try:
            entry_fees_percentage = float(entry_fees_percentage)
        except Exception:
            raise ValueError(f"Invalid entry_fees_percentage : {entry_fees_percentage}")
        if entry_fees_percentage < 0:
            raise ValueError("entry_fees_percentage must be >= 0")

        try:
            exit_fees_percentage = float(exit_fees_percentage)
        except Exception:
            raise ValueError(f"Invalid exit_fees_percentage : {exit_fees_percentage}")
        if exit_fees_percentage < 0:
            raise ValueError("exit_fees_percentage must be >= 0")

        out_orders = orders.copy()
        out_positions = positions.copy()


        #find all executable orders
        mask_pending_orders = out_orders["order_status"] == "PENDING"
        if out_orders[mask_pending_orders].shape[0] > 0 :
            for i in range(len(out_orders[mask_pending_orders])):
                entry_price = out_orders.loc[mask_pending_orders,"order_entry_price"].iloc[i]
                if entry_price >= stockData["Low"].iloc[-1] and entry_price <= stockData["High"].iloc[-1]:
                    #execute orders
                    response = exec_order(order_id = out_orders.loc[mask_pending_orders,"order_id"].iloc[i],
                                          orders = out_orders,
                                          entry_fees_percentage=entry_fees_percentage,
                                          stockData=stockData,
                                          positions=out_positions,
                                          )
                    if not response.get("success"):
                        raise ValueError(response.get("error_message"))
                    out_orders = response.get("orders", out_orders)
                    out_positions = response.get("positions", out_positions)
        mask_open_positions = out_positions["position_status"] == "OPEN"
        open_positions_df = out_positions[mask_open_positions]
        if open_positions_df.shape[0] > 0:
            """
            4 cases :
            + only sl inside low-high range -> execute sl
            + only tp inside low-high range -> execute tp
            + both sl and tp inside low-high range -> exceute tp or sl randomly
            + nothing inside low-high range -> execute nothing
            """
            low = stockData["Low"].iloc[-1]
            high = stockData["High"].iloc[-1]
            for i in range(len(open_positions_df)) :
                position_sl = open_positions_df["position_sl"].iloc[i]
                position_tp = open_positions_df["position_tp"].iloc[i]
                #case both None
                if position_sl is None and position_tp is None :
                    continue
                #position_side = open_positions_df["position_side"].iloc[i]
                #case both
                if position_sl is not None and position_tp is not None :
                    #case both inside low-high range for LONG position
                    if position_sl >= low and position_sl <= high and position_tp >= low and position_tp <= high :
                        rand_decision = random.randint(0, 1)
                        response = exit_position(position_id=open_positions_df["position_id"].iloc[i],
                                                 positions=out_positions,
                                                 stockData=stockData,
                                                 exit_fees_percentage=exit_fees_percentage,
                                                 exit_price=position_tp,
                                                 exit_status="CLOSED_TP",
                                                 ) if rand_decision == 1 else exit_position(
                                                 position_id=open_positions_df["position_id"].iloc[i],
                                                 positions=out_positions,
                                                 stockData=stockData,
                                                 exit_fees_percentage=exit_fees_percentage,
                                                 exit_price=position_sl,
                                                 exit_status="CLOSED_SL",
                                                 )
                        if not response.get("success"):
                            raise ValueError(response.get("error_message"))
                        out_positions = response.get("positions", out_positions)
                        continue
                #case sl only
                if position_sl is not None :
                    if position_sl >= low and position_sl <= high :
                        response = exit_position(position_id=open_positions_df["position_id"].iloc[i],
                                                        positions=out_positions,
                                                        stockData=stockData,
                                                        exit_fees_percentage=exit_fees_percentage,
                                                        exit_price=position_sl,
                                                        exit_status="CLOSED_SL",
                                                        )
                        if not response.get("success"):
                            raise ValueError(response.get("error_message"))
                        out_positions = response.get("positions", out_positions)
                        continue
                #case tp only
                if position_tp is not None :
                    if position_tp >= low and position_tp <= high :
                        response = exit_position(position_id=open_positions_df["position_id"].iloc[i],
                                                        positions=out_positions,
                                                        stockData=stockData,
                                                        exit_fees_percentage=exit_fees_percentage,
                                                        exit_price=position_tp,
                                                        exit_status="CLOSED_TP",
                                                        )
                        if not response.get("success"):
                            raise ValueError(response.get("error_message"))
                        out_positions = response.get("positions", out_positions)
        #update unrealized pnl for open positions
        current_price = float(stockData["Close"].iloc[-1])
        open_mask = out_positions["position_status"] == "OPEN"
        if open_mask.any():
            entry_price = out_positions.loc[open_mask, "position_entry_price"].astype(float)
            quantity = out_positions.loc[open_mask, "position_quantity"].astype(float)
            side = out_positions.loc[open_mask, "position_side"]
            pnl_long = (current_price - entry_price) * quantity
            pnl_short = (entry_price - current_price) * quantity
            out_positions.loc[open_mask, "result_pnl_gross"] = pnl_long.where(side == "LONG", pnl_short)
        return {
            "orders" : out_orders,
            "positions" : out_positions,
            "success" : True,
        }       
    except Exception as e:
        return {
            "orders" : out_orders,
            "positions" : out_positions,
            "success" : False,
            "error_message" : str(e),
            "error_type": type(e).__name__,
            "error_trace": traceback.format_exc(),
        }
