package com.dyq.cafedeficiencias.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * Guarda el historial de diagnósticos realizados. Útil para que el grupo
 * de investigación pueda revisar resultados y para hacer seguimiento del
 * desempeño del modelo en campo (no solo en el set de validación).
 */
@Entity
@Table(name = "diagnosticos")
public class Diagnostico {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String deficienciaDetectada;

    private Double confianza;

    private LocalDateTime fecha;

    // Opcional: útil si más adelante quieren asociar el diagnóstico a una finca/parcela
    private String ubicacion;

    public Diagnostico() {
    }

    public Diagnostico(String deficienciaDetectada, Double confianza, LocalDateTime fecha, String ubicacion) {
        this.deficienciaDetectada = deficienciaDetectada;
        this.confianza = confianza;
        this.fecha = fecha;
        this.ubicacion = ubicacion;
    }

    public Long getId() {
        return id;
    }

    public String getDeficienciaDetectada() {
        return deficienciaDetectada;
    }

    public void setDeficienciaDetectada(String deficienciaDetectada) {
        this.deficienciaDetectada = deficienciaDetectada;
    }

    public Double getConfianza() {
        return confianza;
    }

    public void setConfianza(Double confianza) {
        this.confianza = confianza;
    }

    public LocalDateTime getFecha() {
        return fecha;
    }

    public void setFecha(LocalDateTime fecha) {
        this.fecha = fecha;
    }

    public String getUbicacion() {
        return ubicacion;
    }

    public void setUbicacion(String ubicacion) {
        this.ubicacion = ubicacion;
    }
}