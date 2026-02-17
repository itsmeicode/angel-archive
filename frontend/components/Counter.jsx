import api from "../src/services/api";
import { Typography } from "@mui/material";

export function Counter({ userId, angelId, count, onChange }) {
    const updateUserCollection = async (newCount) => {
        try {
            if (newCount === 0) {
                await api.collections.delete(userId, angelId);
            } else {
                await api.collections.upsert(userId, {
                    angel_id: angelId,
                    count: newCount,
                    is_favorite: false,
                    in_search_of: false,
                    willing_to_trade: false,
                });
            }
        } catch (error) {
            console.error("Error updating user_collections:", error);
        }
    };

    const handleDecrement = async () => {
        const newCount = Math.max((Number(count) || 0) - 1, 0);
        onChange?.(newCount);
        updateUserCollection(newCount);
    };

    const handleIncrement = async () => {
        const newCount = (Number(count) || 0) + 1;
        onChange?.(newCount);
        updateUserCollection(newCount);
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

