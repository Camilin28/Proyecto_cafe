import 'dart:convert';
import 'dart:io';
import 'package:http/http.dart' as http;
import '../models/diagnostico.dart';
import '../models/registro_historial.dart';

class ApiService {
  // Cambia esto por la URL real del backend cuando esté desplegado.
  // En el emulador de Android, "10.0.2.2" apunta al localhost de tu máquina.
  static const String baseUrl = "http://192.168.1.80:8080/api/diagnostico";

  Future<Diagnostico> diagnosticar(File imagen) async {
    final uri = Uri.parse(baseUrl);
    final request = http.MultipartRequest('POST', uri)
      ..files.add(await http.MultipartFile.fromPath('imagen', imagen.path));

    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);

    if (response.statusCode == 200) {
      final json = jsonDecode(response.body) as Map<String, dynamic>;
      return Diagnostico.fromJson(json);
    } else {
      throw Exception('Error del servidor: ${response.statusCode} ${response.body}');
    }
  }

  Future<List<RegistroHistorial>> obtenerHistorial() async {
    final uri = Uri.parse('$baseUrl/historial');
    final response = await http.get(uri);

    if (response.statusCode == 200) {
      final List<dynamic> lista = jsonDecode(response.body) as List<dynamic>;
      return lista
          .map((item) => RegistroHistorial.fromJson(item as Map<String, dynamic>))
          .toList();
    } else {
      throw Exception('Error del servidor: ${response.statusCode} ${response.body}');
    }
  }
}