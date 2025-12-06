import React from "react";
import { Box, Paper, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { SignUpForm } from "../components/SignUpForm";

export default function SignUpPage() {
    const navigate = useNavigate();

    return (
        <Box
            display="flex"
            justifyContent="center"
            alignItems="center"
            height="100vh" 
            flexDirection="column"
            overflow="hidden" 
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
                    Create an Account
                </Typography>

                <SignUpForm />

                <Typography variant="body2" sx={{ marginTop: 2 }}>
                    Already have an account?{" "}
                    <Typography
                        component="span"
                        sx={{ color: "primary.main", fontWeight: "bold", cursor: "pointer" }}
                        onClick={() => navigate("/login")}
                    >
                        Log in!
                    </Typography>
                </Typography>
            </Paper>
        </Box>
    );
}

