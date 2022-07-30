import React, { useContext, useState } from "react";
import config from "../config";
import { useNavigate } from "react-router-dom";

export const Login = () => {
  const [loginForm, setLoginForm] = useState({
    email: "",
    password: "",
  });
  const navigate = useNavigate();

  const saveLoginForm = async () => {
    const response = await fetch(`${config.hostname}/login`, {
      method: "post",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(loginForm),
    });

    if (response.status !== 200) {
      alert("[ERROR] Email or password");
      return;
    }

    const data = await response.json();
    localStorage.token = data;
    navigate("/task");
  };

  const onChangeLoginForm = (key, value) => {
    const data = { ...loginForm, [key]: value };
    setLoginForm(data);
  };

  return (
    <div className="text-center mt-5">
      <h1>Login</h1>
      <div>
        <input
          type="text"
          placeholder="Email:"
          onChange={(e) => onChangeLoginForm("email", e.target.value)}
        />
        <input
          type="password"
          placeholder="Password:"
          onChange={(e) => onChangeLoginForm("password", e.target.value)}
        />
        <button onClick={saveLoginForm}>Save</button>
      </div>
    </div>
  );
};
