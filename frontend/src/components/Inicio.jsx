import React, { useState, useEffect } from 'react';
import axios from 'axios';

function Inicio() {
  axios.defaults.headers.common['Authorization'] = 'Token YOUR_TOKEN_HERE';
  axios.defaults.withCredentials = true;
  const [comunidades, setComunidades] = useState([]);
  const [proyectos, setProyectos] = useState([]);
  const [desafios, setDesafios] = useState([]);

  
  useEffect(() => {
    axios.get('http://localhost:8000/')
      .then(response => {
        setComunidades(response.data.comunidades);
        setProyectos(response.data.proyectos);
        setDesafios(response.data.desafios);
      })
      .catch(error => {
        console.error('Error:', error);
      });
  }, []);

  const renderComunidad = (comunidad) => (
    <li key={comunidad.id}>
      <a href={`/comunidades/${comunidad.id}`}>
        {comunidad.nombre}
      </a>
    </li>
  );

  const renderProyecto = (proyecto) => (
    <li key={proyecto.id}>
      <a href={`/proyectos/${proyecto.id}`}>
        {proyecto.titulo}
      </a>
    </li>
  );

  const renderDesafio = (desafio) => (
    <li key={desafio.id}>
      <a href={`/desafios/${desafio.id}`}>
        {desafio.titulo}
      </a>
    </li>
  );

  return (
    <div className="container">
      <h1 className="main-title">Bienvenido a Hubinab Reward</h1>
      
      <div className="grid-container">
        <section className="card">
          <h2>Tus Comunidades</h2>
          <ul className="list">
            {comunidades.map(renderComunidad)}
            {!comunidades.length && <li>No perteneces a ninguna comunidad activa aún.</li>}
          </ul>
        </section>

        <section className="card">
          <h2>Proyectos Recientes</h2>
          <ul className="list">
            {proyectos.map(renderProyecto)}
            {!proyectos.length && <li>No hay proyectos recientes.</li>}
          </ul>
        </section>

        <section className="card">
          <h2>Desafíos Activos</h2>
          <ul className="list">
            {desafios.map(renderDesafio)}
            {!desafios.length && <li>No hay desafíos activos.</li>}
          </ul>
        </section>
      </div>

      <br />
      <div className="text-center">
        <a href="/crear-publicacion" className="btn btn-primary btn-lg">Crear Publicación</a>
      </div>
    </div>
  );
}

export default Inicio;