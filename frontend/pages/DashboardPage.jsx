import { SonnyAngelMain } from "../components/SonnyAngelMain";
import { Box } from "@mui/material";

export function DashboardPage() {
  return (
    <Box
      sx={{
        height: "100vh",
        overflow: "hidden",
        backgroundImage: "url('/src/assets/AngelArchiveBackground4.jpg')",
        backgroundSize: "100% auto",
        backgroundPosition: "center",
        backgroundRepeat: "repeat",
      }}
    >
      <Box
        sx={{
          height: "100vh",
          overflowY: "auto",
          padding: "20px",
        }}
      >
        <SonnyAngelMain />
      </Box>
    </Box>
  );
}

