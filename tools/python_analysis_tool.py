import ast
import pandas as pd


class UnsafeCodeError(Exception):
    pass


def _ensure_safe(code: str) -> None:
    """Basic AST-based safety checks to block obvious unsafe operations.

    This is not a full sandbox — it blocks imports and common dangerous
    callables (open, exec, eval, __import__, subprocess, os.system, etc.).
    """
    forbidden_names = {
        "open",
        "exec",
        "eval",
        "__import__",
        "compile",
        "input",
        "exit",
        "quit",
    }

    forbidden_modules = {
        "os",
        "sys",
        "subprocess",
        "socket",
        "shutil",
        "requests",
        "urllib",
        "pathlib",
    }

    try:
        tree = ast.parse(code)
    except Exception as e:
        raise UnsafeCodeError(f"Code parse error: {e}")

    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            raise UnsafeCodeError("Import statements are not allowed.")

        if isinstance(node, ast.Call):
            # Get the function name being called if it's a simple Name
            func = node.func
            if isinstance(func, ast.Name):
                if func.id in forbidden_names:
                    raise UnsafeCodeError(f"Use of '{func.id}' is not allowed.")
            elif isinstance(func, ast.Attribute):
                # attribute like os.system or subprocess.call
                # get the root name
                root = func
                while isinstance(root, ast.Attribute):
                    root = root.value
                if isinstance(root, ast.Name) and root.id in forbidden_modules:
                    raise UnsafeCodeError(f"Calls to module '{root.id}' are not allowed.")


class PythonAnalysisTool:

    def run(
        self,
        code,
        datastore
    ):

        code = code.replace(
            "import pandas as pd;",
            ""
        )

        code = code.replace(
            "import pandas as pd",
            ""
        )

        customers = (
            datastore.get_table(
                "customers"
            )
        )

        orders = (
            datastore.get_table(
                "orders"
            )
        )

        orderitems = (
            datastore.get_table(
                "orderitems"
            )
        )

        payments = (
            datastore.get_table(
                "payments"
            )
        )

        products = (
            datastore.get_table(
                "products"
            )
        )

        # Helper utilities available to executed code. These helpers make it
        # easier for generated code to handle string IDs, missing values,
        # and numeric conversions without asking the orchestrator about data.
        def to_numeric(series):
            return pd.to_numeric(series, errors="coerce")

        def safe_nlargest(df, by, n=5):
            """Return top-n rows by column `by` with safe numeric coercion.

            If the column doesn't exist, or numeric coercion yields no valid
            values, returns the first `n` rows as a fallback.
            """
            if by not in df.columns:
                return df.head(n)
            ser = pd.to_numeric(df[by], errors="coerce")
            if ser.notna().sum() == 0:
                return df.head(n)
            idx = ser.nlargest(n).index
            return df.loc[idx]

        def safe_head(df, n=5):
            try:
                return df.head(n)
            except Exception:
                return df

        # Helper to return summary of available data
        tables_dict = {
            'customers': customers,
            'orders': orders,
            'orderitems': orderitems,
            'payments': payments,
            'products': products,
        }

        def get_data_summary():
            """Return a summary of available tables: names, shapes, and columns."""
            summary = {}
            for name, df in tables_dict.items():
                try:
                    summary[name] = {
                        'shape': list(df.shape),  # (rows, cols)
                        'columns': list(df.columns),
                    }
                except Exception:
                    pass
            return summary

        local_vars = {
            "pd": pd,
            "to_numeric": to_numeric,
            "safe_nlargest": safe_nlargest,
            "safe_head": safe_head,
            "get_data_summary": get_data_summary,

            "customers": customers,

            "orders": orders,

            "orderitems": orderitems,

            "payments": payments,

            "products": products,
        }

        # Basic safety check
        try:
            _ensure_safe(code)
        except UnsafeCodeError as e:
            return f"Execution Error: Unsafe code: {e}"

        try:
            exec(code, {}, local_vars)
        except Exception as e:
            return f"Execution Error: {e}"

        result = local_vars.get("result")

        # Serialize common pandas/numpy types into JSON-friendly strings
        try:
            import numpy as np

            if isinstance(result, pd.Series):
                return result.reset_index()

            if hasattr(result, "to_json"):
                # DataFrame or Series
                try:
                    return result.to_json(orient="records")
                except Exception:
                    # fallback to string
                    return str(result)

            if isinstance(result, (list, dict)):
                import json

                return json.dumps(result)

            if isinstance(result, (np.generic,)):
                return result.item()

            return result
        except Exception:
            return str(result)