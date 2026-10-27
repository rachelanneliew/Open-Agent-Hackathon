-- Native rules. LIST first: constraint rule names are the constrained columns.
LIST DQ USL lightning.metastore.dispute_usl_v1.dispute_resolution_usl;
RUN DQ dispute_id TABLE lightning.metastore.dispute_usl_v1.dispute_resolution_usl.merchant_evidence;
RUN DQ current_dispute_id TABLE lightning.metastore.dispute_usl_v1.dispute_resolution_usl.prior_case;
SHOW DQ ALL INVALID TABLE lightning.metastore.dispute_usl_v1.dispute_resolution_usl.merchant_evidence;
SHOW DQ ALL INVALID TABLE lightning.metastore.dispute_usl_v1.dispute_resolution_usl.prior_case;
