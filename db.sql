
-- Table structure for table subscribers
CREATE TABLE IF NOT EXISTS subscribers (
  id SERIAL PRIMARY KEY,
  phone VARCHAR(20),
  status INT DEFAULT 0,
  last_delivered_at TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP,
  UNIQUE (phone, status)
);
