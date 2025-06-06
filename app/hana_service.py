from hdbcli import dbapi
import requests
import json

def obtener_datos_hana(cardcode):
    base = "SB1CSL"
    conn = None
    consulta = f'''
    SELECT
        T0."U_CodigoAgrupador",
        T1."GroupName",
        T0."E_Mail",
        T0."CardCode",
        T0."CardName",
        T0."U_Almacen",
        T0."Phone1",
        CASE
            WHEN T0."QryGroup1" = 'Y' AND T0."QryGroup2" = 'Y' THEN 'CREDITO Y CONTADO'
            WHEN T0."QryGroup1" = 'Y' THEN 'CONTADO'
            WHEN T0."QryGroup2" = 'Y' THEN 'CREDITO'
            ELSE 'NO ENCONTRADO'
        END as "Tipo de cliente"
    FROM
        {base}.OCRD T0
        INNER JOIN {base}.OCRG T1 ON T0."GroupCode" = T1."GroupCode"
    WHERE
        T0."CardType" = 'C'
        AND T0."CardCode" >= '100000'
        AND T0."CardCode" <= '200000'
        AND T0."validFor" = 'Y'
        AND T0."CardCode" = '{cardcode}'
    GROUP BY
        T0."CardCode",
        T0."CardName",
        T1."GroupName",
        T0."E_Mail",
        T0."U_CodigoAgrupador",
        T0."U_Almacen",
        T0."Phone1",
        T0."QryGroup1",
        T0."QryGroup2"
    ORDER BY
        T0."U_CodigoAgrupador" ASC,
        T0."CardCode" ASC
    '''

    try:
        conn = dbapi.connect(
            address='172.16.21.249',
            port=30015,
            user='SYSTEM',
            password='B1AdminH2'
        )
        cursor = conn.cursor()
        cursor.execute(consulta)
        resultados = cursor.fetchall()
        columnas = [desc[0] for desc in cursor.description]
        return [dict(zip(columnas, fila)) for fila in resultados]
    except Exception as e:
        return {'error': str(e)}
    finally:
        if conn:
            conn.close()

def login_sap():
    url = "http://hanab1:50001/b1s/v1/Login"

    payload = json.dumps({
        "CompanyDB": "SB1CSL_TEST",
        "Password": "mana1",
        "UserName": "manager"
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    return    response.json()