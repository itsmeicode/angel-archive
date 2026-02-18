import React, { useState } from "react";
import { Box, TextField, Autocomplete } from "@mui/material";

const sectionStyle = {
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  width: "100%",
};

export function SearchBar({ options, onSearch }) {
  const [inputValue, setInputValue] = useState("");

  const handleInputChange = (event, newInputValue) => {
    setInputValue(newInputValue);
    onSearch(newInputValue);
  };

  const limitedOptions = options.slice(0, 5);

  return (
    <Box sx={{ ...sectionStyle, mb: 2 }}>
      <Autocomplete
        freeSolo
        options={options}
        inputValue={inputValue}
        onInputChange={handleInputChange}
         ListboxProps={{
          style: {
            maxHeight: 125,
            overflowY: "auto",
          },
        }}
        sx={{
          width: { xs: "90%", sm: "60%", md: "40%" },
          "& .MuiInputBase-root": {
            backgroundColor: "pink",
            borderRadius: "8px",
            padding: "6px 10px",
            fontSize: { xs: "0.9rem", sm: "1rem" },
          },
          "& .MuiOutlinedInput-notchedOutline": {
            border: "none",
          },
        }}
        renderInput={(params) => (
          <TextField
            {...params}
            placeholder="Search..."
            variant="outlined"
          />
        )}
      />
    </Box>
  );
}

