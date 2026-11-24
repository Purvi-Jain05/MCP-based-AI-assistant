import pandas as pd


class DataStore:

    def __init__(self):

        customers = pd.read_csv(
            "data/df_Customers.csv"
        )

        orders = pd.read_csv(
            "data/df_Orders.csv"
        )

        orderitems = pd.read_csv(
            "data/df_OrderItems.csv"
        )

        payments = pd.read_csv(
            "data/df_Payments.csv"
        )

        products = pd.read_csv(
            "data/df_Products.csv"
        )

        date_cols = [
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_timestamp",
            "order_estimated_delivery_date"
        ]

        for col in date_cols:

            orders[col] = pd.to_datetime(
                orders[col],
                errors="coerce"
            )

        self.tables = {

            "customers": customers,

            "orders": orders,

            "orderitems": orderitems,

            "payments": payments,

            "products": products
        }

    def get_table(
        self,
        table_name
    ):

        return self.tables[
            table_name
        ]

    def get_schema(
        self
    ):

        schema = {}

        for name, df in self.tables.items():

            schema[name] = list(
                df.columns
            )

        return schema
    
    def get_metadata(
        self
    ):

        metadata = {}

        for name, df in self.tables.items():

            metadata[name] = {

                "rows": len(df),

                "columns": list(
                    df.columns
                ), 

                "dtypes": {

                    col: str(dtype)

                    for col, dtype in (
                        df.dtypes.items()
                    )
                },

                "null_counts": {

                    col: int(
                        df[col]
                        .isna()
                        .sum()
                    )

                    for col in df.columns
                },

                "sample_rows": (

                    df.head(3)
                    .astype(str)
                    .to_dict(
                        orient="records"
                    )
                ),

                "unique_values": {

                    col: (
                        df[col]
                        .dropna()
                        .astype(str)
                        .unique()[:5]
                        .tolist()
                    )

                    for col in df.columns

                    if df[col].dtype == "object"
                }
            }

        return metadata