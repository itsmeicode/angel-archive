import React, { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { TextField, Button, Typography, Paper, Box, } from "@mui/material";
import { LoginForm } from "../components/LogInForm";

export default function LoginPage() {
    const navigate = useNavigate();
    return (
        <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            minHeight="100vh"
            flexDirection="column"
            sx={{
                backgroundImage: "url('/src/assets/AngelArchiveBackground2.jpg')",
                backgroundSize: "cover",
                backgroundPosition: "center",
                backgroundRepeat: "no-repeat",
                padding: 2,
            }}
        >
            <Paper 
                elevation={6} 
                sx={{
                    padding: { xs: 3, sm: 4 },
                    borderRadius: 4,
                    backgroundColor: "rgba(255, 255, 255, 0.8)",
                    textAlign: "center",
                    width: "90%", 
                    maxWidth: "400px", 
                    backdropFilter: "blur(10px)",
                }}
            >
                <Typography 
                    variant="h5"
                    gutterBottom
                    sx={{ 
                        fontWeight: 700, 
                        color: "primary.main",
                        fontSize: { xs: "1.5rem", sm: "2rem" }, 
                        textAlign: "center",
                    }}
                >
                    Log In
                </Typography>

                <LoginForm />

                <Typography variant="body2" sx={{ marginTop: 2 }}>
                    Don't have an account?{" "}
                    <Typography
                        component="span"
                        sx={{ color: "primary.main", fontWeight: "bold", cursor: "pointer" }}
                        onClick={() => navigate("/signup")}
                    >
                        Sign up!
                    </Typography>
                </Typography>
            </Paper>
        </Box>
    );
}

