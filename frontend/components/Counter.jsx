import { Typography } from "@mui/material";

export function Counter({ count, onChange }) {
    const handleDecrement = async () => {
        const newCount = Math.max((Number(count) || 0) - 1, 0);
        onChange?.(newCount);
    };

    const handleIncrement = async () => {
        const newCount = (Number(count) || 0) + 1;
        onChange?.(newCount);
    };

    return (
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Typography
                component="span"
                sx={{
                    color: "primary.dark", 
                    fontWeight: "bold", 
                    cursor: "pointer", 
                    fontSize: "24px", 
                    padding: "0 12px"
                }}
                onClick={handleDecrement}
            >
                -
            </Typography>
            
            <span style={{ margin: "0 10px", fontSize: "22px", fontWeight: "600", color: "black" }}>
                {Number(count) || 0}
            </span> 

            <Typography
                component="span"
                sx={{
                    color: "primary.dark", 
                    fontWeight: "bold", 
                    cursor: "pointer", 
                    fontSize: "24px", 
                    padding: "0 12px"
                }}
                onClick={handleIncrement}
            >
                +
            </Typography>
        </div>
    );
}

