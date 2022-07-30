import React, { useContext, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import config from "../config";

export const Task = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!localStorage.token) {
      navigate("/");
    }
    setLoading(false);
  }, []);

  const onSave = async () => {
    const form = document.getElementById("form");
    const formData = new FormData(form);

    const response = await fetch(`${config.hostname}/task`, {
      method: "post",
      headers: {
        authorization: `Bearer ${localStorage.token}`,
      },
      body: formData,
    });

    if (response.status != 201) {
      alert("Error to save the task");
      return;
    }

    const data = await response.json();
    console.log({ data });
  };

  if (loading)
    return (
      <>
        <div>Cargando...</div>
      </>
    );

  return (
    <div className="text-center mt-5">
      <h1>Task</h1>
      <form id="form">
        <input type="file" name="image" id="image" />
        <input type="text" name="text" id="text" />
      </form>
      <button onClick={onSave}>Submit</button>
    </div>
  );
};
