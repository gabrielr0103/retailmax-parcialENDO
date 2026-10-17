-- Tabla donde el pipeline deja las ventas semanales agregadas.
CREATE SCHEMA IF NOT EXISTS analitica;

CREATE TABLE analitica.ventas_semanales (
    semana             DATE          NOT NULL,
    pais               CHAR(2)       NOT NULL,
    tienda_id          VARCHAR(10)   NOT NULL,
    categoria          VARCHAR(20)   NOT NULL,
    unidades_vendidas  INTEGER       NOT NULL CHECK (unidades_vendidas >= 0),
    precio_unitario    NUMERIC(10,2) NOT NULL CHECK (precio_unitario > 0),
    cargado_en         TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (semana, tienda_id, categoria)
);
