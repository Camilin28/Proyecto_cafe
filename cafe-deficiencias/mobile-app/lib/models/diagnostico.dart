class Diagnostico {
  final String deficiencia;
  final double confianza;
  final Map<String, double> probabilidades;

  Diagnostico({
    required this.deficiencia,
    required this.confianza,
    required this.probabilidades,
  });

  factory Diagnostico.fromJson(Map<String, dynamic> json) {
    final probsJson = json['probabilidades'] as Map<String, dynamic>? ?? {};
    return Diagnostico(
      deficiencia: json['deficiencia'] as String,
      confianza: (json['confianza'] as num).toDouble(),
      probabilidades: probsJson.map(
        (clave, valor) => MapEntry(clave, (valor as num).toDouble()),
      ),
    );
  }
}