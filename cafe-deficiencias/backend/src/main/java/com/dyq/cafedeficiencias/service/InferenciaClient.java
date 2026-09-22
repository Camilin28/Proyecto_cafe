package com.dyq.cafedeficiencias.service;

import com.dyq.cafedeficiencias.dto.PrediccionResponse;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpEntity;
import org.springframework.http.HttpHeaders;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.RestTemplate;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;

/**
 * Habla con el microservicio Python (FastAPI) que carga el modelo entrenado.
 * Así el backend Spring Boot no necesita saber nada de TensorFlow: solo
 * orquesta la petición y guarda el resultado.
 */
@Component
public class InferenciaClient {

    private final RestTemplate restTemplate;

    @Value("${inferencia.service.url:http://localhost:8000}")
    private String inferenciaUrl;

    public InferenciaClient(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    public PrediccionResponse predecir(MultipartFile imagen) throws IOException {
        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.MULTIPART_FORM_DATA);

        MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
        ByteArrayResource recurso = new ByteArrayResource(imagen.getBytes()) {
            @Override
            public String getFilename() {
                return imagen.getOriginalFilename();
            }
        };
        body.add("file", recurso);

        HttpEntity<MultiValueMap<String, Object>> requestEntity = new HttpEntity<>(body, headers);

        return restTemplate.postForObject(
                inferenciaUrl + "/predict",
                requestEntity,
                PrediccionResponse.class
        );
    }
}