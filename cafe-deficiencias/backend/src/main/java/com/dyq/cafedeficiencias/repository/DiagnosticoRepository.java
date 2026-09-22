package com.dyq.cafedeficiencias.repository;

import com.dyq.cafedeficiencias.model.Diagnostico;
import org.springframework.data.jpa.repository.JpaRepository;

public interface DiagnosticoRepository extends JpaRepository<Diagnostico, Long> {
}