import sys, zipfile, pandas as pd, numpy as np

def load(path):
    if path.lower().endswith(".zip"):
        with zipfile.ZipFile(path) as z:
            name=next(n for n in z.namelist() if n.lower().endswith(".csv"))
            with z.open(name) as f: return pd.read_csv(f, encoding="latin1", low_memory=False)
    return pd.read_csv(path, encoding="latin1", low_memory=False)

def build(path, output="14_Category_Distance_Analysis.xlsx"):
    df=load(path); low={c.lower():c for c in df.columns}
    def find(opts): return next((low[o.lower()] for o in opts if o.lower() in low),None)
    order=find(["Order Id"]); cat=find(["Category Name","Product Category","Category"]); delivery=find(["Delivery Status"]); real=find(["Days for shipping (real)"]); sched=find(["Days for shipment (scheduled)"])
    if not all([order,cat,delivery,real,sched]): raise ValueError("Required fields missing; check Order Id, category, Delivery Status and duration fields.")
    df[real]=pd.to_numeric(df[real],errors="coerce"); df[sched]=pd.to_numeric(df[sched],errors="coerce")
    df["__eligible"]=df[delivery].isin(["Advance shipping","Shipping on time","Late delivery"]); df["__ontime"]=df[delivery].isin(["Advance shipping","Shipping on time"]); df["__late"]=df[delivery].eq("Late delivery"); df["__cancel"]=df[delivery].eq("Shipping canceled"); df["__delay"]=df[real]-df[sched]
    g=df.groupby(cat,dropna=False).agg(item_rows=(order,"size"),distinct_orders=(order,"nunique"),eligible_delivered_item_rows=("__eligible","sum"),on_time_item_rows=("__ontime","sum"),late_item_rows=("__late","sum"),shipping_cancelled_item_rows=("__cancel","sum"),avg_delivery_duration_days=(real,"mean"),avg_delay_days_proxy=("__delay","mean")).reset_index().rename(columns={cat:"Product Category"})
    g["on_time_rate_item_level_pct"]=np.where(g.eligible_delivered_item_rows>0,g.on_time_item_rows/g.eligible_delivered_item_rows*100,np.nan); g["cancellation_rate_item_level_pct"]=np.where(g.item_rows>0,g.shipping_cancelled_item_rows/g.item_rows*100,np.nan)
    dist=[c for c in df.columns if any(k in c.lower() for k in ["distance","miles","kilometer"])]
    d=pd.DataFrame([["Explicit distance fields",", ".join(dist) if dist else "None found","Do not infer distance from coordinates without an approved method."]],columns=["Check","Result","Notes"])
    defs=pd.DataFrame([["Category unit","Product-item rows; distinct orders also reported","An order can contain multiple categories; rates are item-row rates."],["On-time rule","Advance shipping or Shipping on time","Provisional status-based rule."],["Cancellation rule","Delivery Status = Shipping canceled","Different from Order Status = CANCELED."],["Duration",real,"Confirm field semantics."],["Delay proxy",real+" − "+sched,"Not timestamp-based."],["Distance","Unavailable unless explicit field found and validated","No coordinate-derived distance calculated."]],columns=["Definition","Rule","Caveat"])
    with pd.ExcelWriter(output,engine="openpyxl") as w: g.to_excel(w,sheet_name="Category Analysis",index=False); defs.to_excel(w,sheet_name="Definitions & Rules",index=False); d.to_excel(w,sheet_name="Distance Field Audit",index=False)
    print("Saved",output,"with",len(g),"categories.")
if __name__=="__main__":
    if len(sys.argv)<2: raise SystemExit("Usage: python build_category_distance_analysis.py <cleaned.zip-or-csv> [output.xlsx]")
    build(sys.argv[1],sys.argv[2] if len(sys.argv)>2 else "14_Category_Distance_Analysis.xlsx")
