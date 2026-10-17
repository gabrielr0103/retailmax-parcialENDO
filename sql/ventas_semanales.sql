-- Ventas semanales por tienda y categoría, base del modelo de predicción.
-- El resultado se guarda como data/raw/ventas_semanales.csv y se versiona con DVC.
-- Parámetros: :fecha_inicio y :fecha_fin (la ficha de procedencia anota los usados).

SELECT
    DATE_TRUNC('week', v.fecha)::date  AS semana,
    t.pais,
    t.tienda_id,
    p.categoria,
    SUM(v.cantidad)                    AS unidades_vendidas,
    ROUND(AVG(v.precio_unitario_usd), 2) AS precio_unitario
FROM ventas.transacciones AS v
JOIN maestros.tiendas   AS t ON t.tienda_id = v.tienda_id
JOIN maestros.productos AS p ON p.sku = v.sku
WHERE v.estado = 'pagada'
  AND v.fecha >= :fecha_inicio
  AND v.fecha <  :fecha_fin
GROUP BY 1, 2, 3, 4
ORDER BY 1, 3, 4;
