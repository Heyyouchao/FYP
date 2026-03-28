# engine/measurements.py

def get_measurements(row, relay):

    try:
        voltage = (
            row[f"{relay}-PM1:V"] +
            row[f"{relay}-PM2:V"] +
            row[f"{relay}-PM3:V"]
        ) / 3 / 1000  # convert to kV

        current = (
            row[f"{relay}-PM4:I"] +
            row[f"{relay}-PM5:I"] +
            row[f"{relay}-PM6:I"]
        ) / 3

        frequency = row[f"{relay}:F"]

        pos = abs(row[f"{relay}-PM7:V"])
        neg = abs(row[f"{relay}-PM8:V"])
        zero = abs(row[f"{relay}-PM9:V"])

        total = pos + neg + zero

        if total > 0:
            pos_pct = pos / total * 100
            neg_pct = neg / total * 100
            zero_pct = zero / total * 100
        else:
            pos_pct = neg_pct = zero_pct = 0

        return {
            "voltage": voltage,
            "current": current,
            "frequency": frequency,
            "pos": pos_pct,
            "neg": neg_pct,
            "zero": zero_pct
        }

    except Exception as e:
        return {"error": str(e)}