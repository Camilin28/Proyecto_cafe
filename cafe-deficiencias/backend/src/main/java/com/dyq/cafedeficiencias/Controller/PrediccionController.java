package com.dyq.cafedeficiencias.controller;

import com.dyq.cafedeficiencias.dto.PrediccionResponse;
import com.dyq.cafedeficiencias.model.Diagnostico;
import com.dyq.cafedeficiencias.repository.DiagnosticoRepository;
import com.dyq.cafedeficiencias.service.PrediccionService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.List;

@RestController
@RequestMapping("/api/diagnostico")
@CrossOrigin(origins = "*") // ajustar en producción / cuando la app móvil esté lista
public class PrediccionController {

    private final PrediccionService prediccionService;
    private final DiagnosticoRepository diagnosticoRepository;

    public PrediccionController(PrediccionService prediccionService, DiagnosticoRepository diagnosticoRepository) {
        this.prediccionService = prediccionService;
        this.diagnosticoRepository = diagnosticoRepository;
    }

    // La app móvil (o un cliente de prueba tipo Postman) sube la foto aquí
    @PostMapping(consumes = "multipart/form-data")
    public ResponseEntity<PrediccionResponse> diagnosticar(
            @RequestParam("imagen") MultipartFile imagen,
            @RequestParam(value = "ubicacion", required = false) String ubicacion
    ) throws IOException {
        PrediccionResponse respuesta = prediccionService.diagnosticar(imagen, ubicacion);
        return ResponseEntity.ok(respuesta);
    }

    // Historial para que el grupo de investigación pueda revisar diagnósticos pasados
    @GetMapping("/historial")
    public ResponseEntity<List<Diagnostico>> historial() {
        return ResponseEntity.ok(diagnosticoRepository.findAll());
    }
}