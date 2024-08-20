CREATE TABLE IF NOT EXISTS urls (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS checks (
    id SERIAL PRIMARY KEY,
    response_code INT,
    h1 VARCHAR(255),
    title VARCHAR(255),
    description VARCHAR(255),
    created_date DATE DEFAULT CURRENT_DATE,
    url_id INT,
    FOREIGN KEY (url_id) REFERENCES urls(id)
);
