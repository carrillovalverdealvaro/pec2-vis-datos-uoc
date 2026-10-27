
import polars as pl

def df_to_tree(df: pl.DataFrame, path_cols: list[str], value_col: str, depth: int = 0) -> list[dict]:
    """
    Convierte un polars DataFrame en un diccionario anidado en vale a las columnas indicadas
    
    Args:
        df(pl.DataFrame): DataFrame del que se va a obtener el diccionario final.
        path_cols(list[str]): Listado de columnas que van a separar la información, en orden de mayor a menor.
        value_col(str): Indicar la columna en la que se tiene el valor que queremos representar de cada children.
        depth(int): Truncar la profundidad del árbol en base a un valor determinado.

    Returns:
        list[dict]: Listado de diccionarios que contienen la información anidada por grupos determinados
    """
    col = path_cols[depth]
    es_hoja = depth == len(path_cols) - 1
    nodos = []
    for (nombre,), grupo in df.group_by(col, maintain_order=True):
        if es_hoja:
            nodos.append({"name": nombre, "value": float(grupo[value_col].sum())})
        else:
            nodos.append({"name": nombre, "children": df_to_tree(grupo, path_cols, value_col, depth + 1)})
    return nodos
