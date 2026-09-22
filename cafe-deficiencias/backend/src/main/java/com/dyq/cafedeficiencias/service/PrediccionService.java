package com.dyq.cafedeficiencias.service;

import com.dyq.cafedeficiencias.dto.PrediccionResponse;
import com.dyq.cafedeficiencias.model.Diagnostico;
import com.dyq.cafedeficiencias.repository.DiagnosticoRepository;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.time.LocalDateTime;

@Service
public class PrediccionService {

    private final InferenciaClient inferenciaClient;
    private final DiagnosticoRepository diagnosticoRepository;

    public PrediccionService(InferenciaClient inferenciaClient, DiagnosticoRepository diagnosticoRepository) {
        this.inferenciaClient = inferenciaClient;
        this.diagnosticoRepository = diagnosticoRepository;
    }

    public PrediccionResponse diagnosticar(MultipartFile imagen, String ubicacion) throws IOException {
        PrediccionResponse resultado = inferenciaClient.predecir(imagen);

        Diagnostico diagnostico = new Diagnostico(
                resultado.getDeficiencia(),
                resultado.getConfianza(),
                LocalDateTime.now(),
                ubicacion
        );
        diagnosticoRepository.save(diagnostico);

        return resultado;
    }
}