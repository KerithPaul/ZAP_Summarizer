CREATE OR REPLACE FUNCTION result_insert_notify()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('new_report', json_build_object('id', NEW.id)::text);
    RETURN NEW;
END;

$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS result_trigger ON zap_results;
CREATE TRIGGER result_trigger
AFTER INSERT ON zap_results
FOR EACH ROW
EXECUTE FUNCTION result_insert_notify();