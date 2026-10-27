-- Requires the fixed fixture service and dedicated immutable CSV copy.
CREATE LIGHTNING DATABASE dispute_merchant_v1 DESCRIBE BY "Synthetic merchant CSV USL preview";
CREATE LIGHTNING FILESTORE TABLE evidence FROM dispute_merchant_v1 FORMAT CSV OPTIONS (
  path "file:///home/zetaris/customer-data/shared/dispute-usl-v1/merchant_evidence.csv",
  header "true", inferSchema "false", delimiter ","
);
CREATE LIGHTNING DATABASE dispute_customer_v1 DESCRIBE BY "Synthetic customer REST USL preview";
CREATE LIGHTNING REST TABLE history_raw FROM dispute_customer_v1 REQUEST (
  endpoint "http://dispute-usl-customer-api-v1:8090/v1/history",
  method "GET", http_encoding "URLENCODED", response_type "JSON", insecure_ssl "false"
) HEADER () BODY ();
