import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Proyectos() {
  const [proyectos, setProyectos] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/proyectos/')
      .then(response => {
        setProyectos(response.data);
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }, []);

  return (
    <div>
      <h1>Proyectos</h1>
      <ul>
        {proyectos.map(proyecto => (
          <li key={proyecto.id}>
            {proyecto.titulo} (Creador: {proyecto.creador.username})
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Proyectos;