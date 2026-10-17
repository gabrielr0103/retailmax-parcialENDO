-- Separa las ventas de tienda física y de e-commerce.
-- Las filas que ya existían quedan como 'tienda', que era el único canal antes de este cambio.
ALTER TABLE analitica.ventas_semanales
    ADD COLUMN canal VARCHAR(10) NOT NULL DEFAULT 'tienda'
    CHECK (canal IN ('tienda', 'ecommerce'));
