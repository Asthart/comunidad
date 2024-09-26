import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Comunidades() {
  const [comunidades, setComunidades] = useState([]);

  useEffect(() => {
    axios.get('http://localhost:8000/comunidades/')
      .then(response => {
        setComunidades(response.data);
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }, []);

  return (
    <div>
      <h1>Comunidades</h1>
      <ul>
        {comunidades.map(comunidad => (
          <li key={comunidad.id}>
            {comunidad.nombre} ({comunidad.miembros.length} miembros)
          </li>
        ))}
      </ul>
    </div>
  );
}

export default Comunidades;