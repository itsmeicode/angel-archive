import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import api from "../src/services/api";
import { fetchAngelsProfileImages } from "../src/utils/queries";
import { useNavigate } from "react-router-dom";
import { TextField, Button, Typography, Paper, CircularProgress, Dialog, Grid, Avatar, Box } from "@mui/material";

export function SignUpForm() {
    const { signUp } = useAuth();
    const navigate = useNavigate();
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [username, setUsername] = useState("");
    const [profilePic, setProfilePic] = useState(null);
    const [errorMessage, setErrorMessage] = useState("");
    const [images, setImages] = useState([]);
    const [loading, setLoading] = useState(true);
    const [popupVisible, setPopupVisible] = useState(false);

    useEffect(() => {
        const loadImages = async () => {
            const angels = await fetchAngelsProfileImages();
            if (angels.length) {
                setImages(angels);
            }
            setLoading(false);
        };
        loadImages();
    }, []);

    const toggleImages = () => {
        setPopupVisible(!popupVisible);
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setErrorMessage("");

        if (!profilePic) {
            setErrorMessage("Please select a profile picture.");
            return;
        }

        if (!email || !password || !username) {
            setErrorMessage("Please fill in all fields.");
            return;
        }

        if (password.length < 8) {
            setErrorMessage("Password must be at least 8 characters.");
            return;
        }

        try {
            const usernameCheck = await api.auth.checkUsername(username);
            if (usernameCheck.exists) {
                setErrorMessage("Username is already taken. Please choose another.");
                return;
            }
        } catch (err) {
            setErrorMessage("Error checking username availability.");
            return;
        }

        try {
            const emailCheck = await api.auth.checkEmail(email);
            if (emailCheck.exists) {
                setErrorMessage("User already created with this email.");
                return;
            }
        } catch (err) {
            setErrorMessage("Error checking email availability.");
            return;
        }

        try {
            const authData = await api.auth.signup({ email, password });
            const userId = authData?.user?.id;

            if (!userId) {
                setErrorMessage("Authentication failed. Please try again.");
                return;
            }

            try {
                await api.auth.createUser({
                    id: userId,
                    email,
                    username,
                    profile_pic: profilePic
                });
                navigate("/login");
            } catch (insertError) {
                setErrorMessage(`Error creating user profile: ${insertError.message}`);
            }
        } catch (signUpError) {
            setErrorMessage(`Sign up error: ${signUpError.message}`);
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
            <Box display="flex" justifyContent="center" mb={2}>
                <Avatar 
                    src={profilePic} 
                    sx={{ 
                        width: 70, 
                        height: 70, 
                        cursor: "pointer",
                        border: "2px solid #ddd",
                    }} 
                    onClick={toggleImages} 
                />
            </Box>
            <Button 
                variant="outlined" 
                fullWidth 
                onClick={toggleImages}
                sx={{ marginBottom: 2 }}
            >
                {profilePic ? "Change Profile Picture" : "Select Profile Picture"}
            </Button>
            <form onSubmit={handleSubmit}>
                <TextField label="Username" fullWidth margin="normal" value={username} onChange={(e) => setUsername(e.target.value)} required />
                <TextField label="Email" type="email" fullWidth margin="normal" value={email} onChange={(e) => setEmail(e.target.value)} required />
                <TextField label="Password" type="password" fullWidth margin="normal" value={password} onChange={(e) => setPassword(e.target.value)} required />
                {errorMessage && <Typography color="error" sx={{ marginBottom: 2 }}>{errorMessage}</Typography>}
                <Button type="submit" variant="contained" color="primary" fullWidth sx={{ mt: 2 }}>Sign Up</Button>
            </form>
            <Dialog 
                open={popupVisible} 
                onClose={() => setPopupVisible(false)} 
                sx={{ 
                    "& .MuiDialog-paper": { 
                        width: "90%", 
                        maxWidth: "800px", 
                        padding: 3,
                        maxHeight: "80vh", 
                        overflowY: "auto" 
                    } 
                }}
            >
                <Box display="flex" flexDirection="column" alignItems="center" p={3}>
                    <Typography 
                        variant="h5"
                        gutterBottom
                        sx={{ 
                            fontWeight: 700, 
                            color: "primary.main",
                            fontSize: { xs: "1.5rem", sm: "2rem" }, 
                            textAlign: "center",
                            marginBottom: 2, 
                        }}
                    >
                        Select a Profile Picture
                    </Typography>
                    {loading ? <CircularProgress /> : (
                        <Grid container spacing={2} justifyContent="center">
                            {images.map((img) => (
                                <Grid 
                                    item 
                                    key={img.id} 
                                    xs={6} 
                                    sm={3} 
                                    onClick={() => { setProfilePic(img.image_url); setPopupVisible(false); }} 
                                    sx={{ 
                                        textAlign: "center", 
                                        cursor: "pointer", 
                                        display: "flex", 
                                        flexDirection: "column", 
                                        alignItems: "center",
                                        justifyContent: "center" 
                                    }}
                                >
                                    <Avatar 
                                        src={img.image_url} 
                                        sx={{ 
                                            width: 90, 
                                            height: 90, 
                                            cursor: "pointer", 
                                            border: "2px solid #ddd",
                                            transition: "all 0.3s",
                                            "&:hover": {
                                                borderColor: "#4CAF50",
                                                transform: "scale(1.1)",
                                            }
                                        }} 
                                    />
                                    <Typography 
                                        variant="body2" 
                                        sx={{ 
                                            marginTop: 1, 
                                            textAlign: "center", 
                                            fontWeight: 500,
                                            fontSize: { xs: "0.875rem", sm: "1rem" } 
                                        }}
                                    >
                                        {img.name}
                                    </Typography>
                                </Grid>
                            ))}
                        </Grid>
                    )}
                </Box>
            </Dialog>
        </Paper>
    );
}

