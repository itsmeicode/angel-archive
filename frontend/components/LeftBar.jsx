import React from "react";
import { Box } from "@mui/material";
import { Sort } from "./Sort";
import { Filter } from "./Filter";

export function LeftBar() {
  return (
    <Box
      bgcolor={"pink"}
      sx={{
        width: "100%",
        height: "calc{100vh - 80px}",
        p: 2,
        overflowY: "auto",
      }}
    >
      <Sort />
      <Filter />
    </Box>
  );
}

