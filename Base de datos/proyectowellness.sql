-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 03-10-2026 a las 03:16:04
-- Versión del servidor: 10.1.38-MariaDB
-- Versión de PHP: 7.3.2

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `proyectowellness`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `conversaciones`
--

CREATE TABLE `conversaciones` (
  `id` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `rol` enum('usuario','asistente') NOT NULL,
  `mensaje` text NOT NULL,
  `fecha` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `estado_animo_actual`
--

CREATE TABLE `estado_animo_actual` (
  `id_estado` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `estado_animo` varchar(30) NOT NULL,
  `fecha_hora` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `lecturas`
--

CREATE TABLE `lecturas` (
  `id_lectura` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_libro` int(11) NOT NULL,
  `estado` enum('por_leer','leyendo','terminado','pausado','He terminado el libro','Sí, continuaré leyendo','No por ahora') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_inicio` datetime DEFAULT NULL,
  `fecha_fin` datetime DEFAULT NULL,
  `paginas_leidas` int(11) DEFAULT '0',
  `capitulos_leidos` int(11) DEFAULT '0',
  `tiempo_minutos` int(11) DEFAULT '0',
  `pagina_actual` int(11) DEFAULT '0',
  `fecha_limite` date DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `libros`
--

CREATE TABLE `libros` (
  `id_libro` int(11) NOT NULL,
  `titulo` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `autor` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci,
  `formato` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `genero` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `es_agregado_manualmente` tinyint(4) DEFAULT NULL,
  `num_caps` int(11) DEFAULT NULL,
  `id_usuario` int(11) NOT NULL,
  `portada` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `categoria` enum('leyendo','pendiente','leido','inconcluso') COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `key_libro` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `paginas_totales` int(11) DEFAULT NULL,
  `id_google` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `anio` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `notas_lectura`
--

CREATE TABLE `notas_lectura` (
  `id_nota` int(11) NOT NULL,
  `id_lectura` int(11) NOT NULL,
  `como_te_sientes` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `que_aprendiste` text COLLATE utf8mb4_unicode_ci,
  `palabras_nuevas` text COLLATE utf8mb4_unicode_ci,
  `personaje_destacado` text COLLATE utf8mb4_unicode_ci,
  `escena_impacto` text COLLATE utf8mb4_unicode_ci,
  `continuara` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `parecer_sesion` text COLLATE utf8mb4_unicode_ci,
  `recuerdo_vida` text COLLATE utf8mb4_unicode_ci,
  `notas_observaciones` text COLLATE utf8mb4_unicode_ci,
  `buscaba_al_leer` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `encontro_lo_buscado` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `tipo_reflexion` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `respuesta_reflexion` text COLLATE utf8mb4_unicode_ci
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `notas_usuario`
--

CREATE TABLE `notas_usuario` (
  `id_nota` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_libro` int(11) DEFAULT NULL,
  `titulo` varchar(255) NOT NULL,
  `contenido` text NOT NULL,
  `categoria` varchar(100) NOT NULL,
  `fecha_creacion` date NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `objetivos_personales`
--

CREATE TABLE `objetivos_personales` (
  `id_objetivo` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `tipo` enum('custom','tiempo_diario','racha_dias','libros','paginas','tiempo','rutina') COLLATE utf8mb4_unicode_ci NOT NULL,
  `meta` int(11) NOT NULL,
  `progreso_actual` int(11) DEFAULT '0',
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date DEFAULT NULL,
  `completado` tinyint(1) DEFAULT '0',
  `genero_objetivo` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '',
  `porcentaje` decimal(5,2) NOT NULL,
  `Logro_objetivo` enum('logro','objetivo') COLLATE utf8mb4_unicode_ci NOT NULL,
  `descripcion` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `titulo` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `unidad` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `condicion_tipo` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `condicion_valor` varchar(100) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `frecuencia` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `estado` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT 'activo'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `preguntas_encuesta`
--

CREATE TABLE `preguntas_encuesta` (
  `id_pregunta` int(11) NOT NULL,
  `nivel` enum('principiante','intermedio','maestro') COLLATE utf8mb4_unicode_ci NOT NULL,
  `texto_pregunta` text COLLATE utf8mb4_unicode_ci NOT NULL,
  `nombre_campo` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `recomendaciones_cache`
--

CREATE TABLE `recomendaciones_cache` (
  `id` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `titulo` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `autor` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `descripcion` text COLLATE utf8mb4_unicode_ci,
  `portada` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `paginas` int(11) DEFAULT NULL,
  `generos` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `anio` varchar(20) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `id_google` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `fecha_generacion` datetime DEFAULT CURRENT_TIMESTAMP,
  `key` varchar(255) COLLATE utf8mb4_unicode_ci DEFAULT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `respuestas_encuesta`
--

CREATE TABLE `respuestas_encuesta` (
  `id_respuesta` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `id_pregunta` int(11) NOT NULL,
  `respuesta` text COLLATE utf8mb4_unicode_ci,
  `fecha` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `sesiones`
--

CREATE TABLE `sesiones` (
  `id_sesion` int(11) NOT NULL,
  `id_lectura` int(11) NOT NULL,
  `id_usuario` int(11) NOT NULL,
  `fecha` datetime DEFAULT NULL,
  `paginas_leidas_sesion` int(11) DEFAULT '0',
  `tiempo_minutos` int(11) DEFAULT '0',
  `capitulos_leidos` int(11) DEFAULT '0',
  `como_te_sientes` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuarios`
--

CREATE TABLE `usuarios` (
  `id_usuario` int(11) NOT NULL,
  `nombre` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `correo` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `password` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
  `nivel_actual` enum('principiante','intermedio','maestro') COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT 'principiante',
  `total_libros_leidos` int(11) DEFAULT '0',
  `total_paginas_leidas` int(11) DEFAULT '0',
  `promedio_paginas_sesion` decimal(5,2) DEFAULT '0.00',
  `genero_preferido` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT '',
  `recomendacion_inicial_generada` tinyint(1) NOT NULL DEFAULT '0',
  `notificaciones_activadas` tinyint(1) DEFAULT '1'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `usuario_encuesta_temporal`
--

CREATE TABLE `usuario_encuesta_temporal` (
  `id_usuario` int(11) NOT NULL,
  `fecha` datetime DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `conversaciones`
--
ALTER TABLE `conversaciones`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `estado_animo_actual`
--
ALTER TABLE `estado_animo_actual`
  ADD PRIMARY KEY (`id_estado`),
  ADD KEY `idx_usuario` (`id_usuario`);

--
-- Indices de la tabla `lecturas`
--
ALTER TABLE `lecturas`
  ADD PRIMARY KEY (`id_lectura`),
  ADD UNIQUE KEY `uk_lectura_usuario` (`id_lectura`,`id_usuario`),
  ADD UNIQUE KEY `unico_libro_usuario` (`id_usuario`,`id_libro`),
  ADD KEY `FK_1` (`id_libro`);

--
-- Indices de la tabla `libros`
--
ALTER TABLE `libros`
  ADD PRIMARY KEY (`id_libro`);

--
-- Indices de la tabla `notas_lectura`
--
ALTER TABLE `notas_lectura`
  ADD PRIMARY KEY (`id_nota`),
  ADD KEY `id_lectura` (`id_lectura`);

--
-- Indices de la tabla `notas_usuario`
--
ALTER TABLE `notas_usuario`
  ADD PRIMARY KEY (`id_nota`),
  ADD KEY `id_usuario` (`id_usuario`),
  ADD KEY `id_libro` (`id_libro`);

--
-- Indices de la tabla `objetivos_personales`
--
ALTER TABLE `objetivos_personales`
  ADD PRIMARY KEY (`id_objetivo`),
  ADD KEY `FK_10` (`id_usuario`);

--
-- Indices de la tabla `preguntas_encuesta`
--
ALTER TABLE `preguntas_encuesta`
  ADD PRIMARY KEY (`id_pregunta`);

--
-- Indices de la tabla `recomendaciones_cache`
--
ALTER TABLE `recomendaciones_cache`
  ADD PRIMARY KEY (`id`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `respuestas_encuesta`
--
ALTER TABLE `respuestas_encuesta`
  ADD PRIMARY KEY (`id_respuesta`),
  ADD KEY `id_usuario` (`id_usuario`),
  ADD KEY `id_pregunta` (`id_pregunta`);

--
-- Indices de la tabla `sesiones`
--
ALTER TABLE `sesiones`
  ADD PRIMARY KEY (`id_sesion`),
  ADD KEY `id_lectura` (`id_lectura`),
  ADD KEY `id_usuario` (`id_usuario`);

--
-- Indices de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`id_usuario`),
  ADD UNIQUE KEY `uk_usuarios_correo` (`correo`);

--
-- Indices de la tabla `usuario_encuesta_temporal`
--
ALTER TABLE `usuario_encuesta_temporal`
  ADD PRIMARY KEY (`id_usuario`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `conversaciones`
--
ALTER TABLE `conversaciones`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `estado_animo_actual`
--
ALTER TABLE `estado_animo_actual`
  MODIFY `id_estado` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `lecturas`
--
ALTER TABLE `lecturas`
  MODIFY `id_lectura` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `libros`
--
ALTER TABLE `libros`
  MODIFY `id_libro` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `notas_lectura`
--
ALTER TABLE `notas_lectura`
  MODIFY `id_nota` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `notas_usuario`
--
ALTER TABLE `notas_usuario`
  MODIFY `id_nota` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `objetivos_personales`
--
ALTER TABLE `objetivos_personales`
  MODIFY `id_objetivo` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `preguntas_encuesta`
--
ALTER TABLE `preguntas_encuesta`
  MODIFY `id_pregunta` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `recomendaciones_cache`
--
ALTER TABLE `recomendaciones_cache`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `respuestas_encuesta`
--
ALTER TABLE `respuestas_encuesta`
  MODIFY `id_respuesta` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `sesiones`
--
ALTER TABLE `sesiones`
  MODIFY `id_sesion` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de la tabla `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `id_usuario` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `estado_animo_actual`
--
ALTER TABLE `estado_animo_actual`
  ADD CONSTRAINT `fk_estado_usuario` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);

--
-- Filtros para la tabla `lecturas`
--
ALTER TABLE `lecturas`
  ADD CONSTRAINT `FK_0` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE,
  ADD CONSTRAINT `FK_1` FOREIGN KEY (`id_libro`) REFERENCES `libros` (`id_libro`) ON DELETE CASCADE;

--
-- Filtros para la tabla `notas_lectura`
--
ALTER TABLE `notas_lectura`
  ADD CONSTRAINT `fk_notas_lectura_lectura` FOREIGN KEY (`id_lectura`) REFERENCES `lecturas` (`id_lectura`) ON DELETE CASCADE;

--
-- Filtros para la tabla `notas_usuario`
--
ALTER TABLE `notas_usuario`
  ADD CONSTRAINT `notas_usuario_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  ADD CONSTRAINT `notas_usuario_ibfk_2` FOREIGN KEY (`id_libro`) REFERENCES `libros` (`id_libro`) ON DELETE CASCADE;

--
-- Filtros para la tabla `objetivos_personales`
--
ALTER TABLE `objetivos_personales`
  ADD CONSTRAINT `FK_10` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`) ON DELETE CASCADE;

--
-- Filtros para la tabla `respuestas_encuesta`
--
ALTER TABLE `respuestas_encuesta`
  ADD CONSTRAINT `respuestas_encuesta_ibfk_1` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`),
  ADD CONSTRAINT `respuestas_encuesta_ibfk_2` FOREIGN KEY (`id_pregunta`) REFERENCES `preguntas_encuesta` (`id_pregunta`);

--
-- Filtros para la tabla `sesiones`
--
ALTER TABLE `sesiones`
  ADD CONSTRAINT `sesiones_ibfk_1` FOREIGN KEY (`id_lectura`) REFERENCES `lecturas` (`id_lectura`) ON DELETE CASCADE,
  ADD CONSTRAINT `sesiones_ibfk_2` FOREIGN KEY (`id_usuario`) REFERENCES `usuarios` (`id_usuario`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
