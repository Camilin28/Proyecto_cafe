class RegistroHistorial {
  final int id;
  final String deficienciaDetectada;
  final double confianza;
  final DateTime fecha;
  final String? ubicacion;

  RegistroHistorial({
    required this.id,
    required this.deficienciaDetectada,
    required this.confianza,
    required this.fecha,
    this.ubicacion,
  });

  factory RegistroHistorial.fromJson(Map<String, dynamic> json) {
    return RegistroHistorial(
      id: json['id'] as int,
      deficienciaDetectada: json['deficienciaDetectada'] as String,
      confianza: (json['confianza'] as num).toDouble(),
      fecha: DateTime.parse(json['fecha'] as String),
      ubicacion: json['ubicacion'] as String?,
    );
  }
}