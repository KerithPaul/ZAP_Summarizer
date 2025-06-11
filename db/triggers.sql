CREATE OR REPLACE FUNCTION report_insert_notify()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('new_report', json_build_object('id', NEW.id)::text);
    RETURN NEW;
END;

$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS report_trigger ON zap_reports;
CREATE TRIGGER report_trigger
AFTER INSERT ON zap_reports
FOR EACH ROW
EXECUTE FUNCTION report_insert_notify();