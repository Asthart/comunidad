import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Desafios() {
  const [desafios, setDesafios] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/desafios/')
      .then(response => {
        setDesafios(response.data);
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }, []);

  return (
    <div>
      <h1>Desafíos</h1>
      <ul>
        {desafios.map(desafio => (
          <li key={desafio.id}>
            {desafio.titulo} (Fecha inicio: {new Date(desafio.fecha_inicio).toLocaleDateString()})
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Desafios;