package com.dyq.cafedeficiencias.dto;

import java.util.Map;

public class PrediccionResponse {

    private String deficiencia;
    private double confianza;
    private Map<String, Double> probabilidades;

    public PrediccionResponse() {
    }

    public PrediccionResponse(String deficiencia, double confianza, Map<String, Double> probabilidades) {
        this.deficiencia = deficiencia;
        this.confianza = confianza;
        this.probabilidades = probabilidades;
    }

    public String getDeficiencia() {
        return deficiencia;
    }

    public void setDeficiencia(String deficiencia) {
        this.deficiencia = deficiencia;
    }

    public double getConfianza() {
        return confianza;
    }

    public void setConfianza(double confianza) {
        this.confianza = confianza;
    }

    public Map<String, Double> getProbabilidades() {
        return probabilidades;
    }

    public void setProbabilidades(Map<String, Double> probabilidades) {
        this.probabilidades = probabilidades;
    }
}