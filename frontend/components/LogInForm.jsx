import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { TextField, Button, Typography, Paper } from "@mui/material";
import { useNavigate } from "react-router-dom";

export function LoginForm() {
    const { signIn } = useAuth();
    const navigate = useNavigate();
    const [identifier, setIdentifier] = useState("");
    const [password, setPassword] = useState("");
    const [errorMessage, setErrorMessage] = useState("");

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrorMessage("");

        if (!identifier || !password) {
            setErrorMessage("Please fill in all fields.");
            return;
        }

        try {
            await signIn(identifier, password);
            navigate("/dashboard");
        } catch (error) {
            setErrorMessage(error.message);
        }
    };

    return (
        <Paper 
            elevation={3} 
            sx={{
                padding: { xs: 2, sm: 3 }, 
                width: "90%", 
                maxWidth: "350px", 
                mx: "auto", 
                mt: 2, 
                textAlign: "center", 
                backgroundColor: "rgba(255, 255, 255, 0.95)",
            }}
        >
            <form onSubmit={handleSubmit}>
                <TextField 
                    label="Email/Username" 
                    type="text" 
                    fullWidth 
                    margin="normal" 
                    value={identifier} 
                    onChange={(e) => setIdentifier(e.target.value)} 
                    required 
                />
                <TextField 
                    label="Password" 
                    type="password" 
                    fullWidth 
                    margin="normal" 
                    value={password} 
                    onChange={(e) => setPassword(e.target.value)} 
                    required 
                />
                {errorMessage && <Typography color="error" sx={{ marginBottom: 2 }}>{errorMessage}</Typography>}
                <Button 
                    type="submit" 
                    variant="contained" 
                    color="primary" 
                    fullWidth 
                    sx={{ mt: 2 }}
                >
                    Log In
                </Button>
            </form>
        </Paper>
    );
}

