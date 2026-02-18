import React from "react";
import { Box } from "@mui/material";
import { Filter } from "./Filter";

export function LeftBar({ onFilterChange }) {
  return (
    <Box
      bgcolor={"pink"}
      sx={{
        width: "100%",
        p: 2,
      }}
    >
      <Filter onFilterChange={onFilterChange} />
    </Box>
  );
}

