import 'dart:io';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'models/diagnostico.dart';
import 'services/api_service.dart';
import 'screens/historial_screen.dart';

void main() {
  runApp(const CafeDeficienciasApp());
}

class CafeDeficienciasApp extends StatelessWidget {
  const CafeDeficienciasApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Deficiencias en Café',
      theme: ThemeData(
        colorSchemeSeed: const Color(0xFF6F4E37),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final ApiService _apiService = ApiService();
  final ImagePicker _picker = ImagePicker();

  File? _imagenSeleccionada;
  Diagnostico? _resultado;
  bool _cargando = false;
  String? _error;

  Future<void> _seleccionarImagen(ImageSource fuente) async {
    final XFile? archivo = await _picker.pickImage(source: fuente, imageQuality: 85);
    if (archivo == null) return;

    setState(() {
      _imagenSeleccionada = File(archivo.path);
      _resultado = null;
      _error = null;
    });

    await _diagnosticar();
  }

  Future<void> _diagnosticar() async {
    if (_imagenSeleccionada == null) return;

    setState(() {
      _cargando = true;
      _error = null;
    });

    try {
      final resultado = await _apiService.diagnosticar(_imagenSeleccionada!);
      setState(() => _resultado = resultado);
    } catch (e) {
      setState(() => _error = 'No se pudo conectar con el servidor. ¿Está corriendo el backend?');
    } finally {
      setState(() => _cargando = false);
    }
  }

  void _abrirHistorial() {
    Navigator.of(context).push(
      MaterialPageRoute(builder: (context) => const HistorialScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Diagnóstico de café'),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            tooltip: 'Historial',
            onPressed: _abrirHistorial,
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Expanded(
              child: Center(
                child: _imagenSeleccionada == null
                    ? const Text('Selecciona o toma una foto de la hoja')
                    : ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: Image.file(_imagenSeleccionada!, fit: BoxFit.cover),
                      ),
              ),
            ),
            if (_cargando) const Padding(
              padding: EdgeInsets.symmetric(vertical: 16),
              child: CircularProgressIndicator(),
            ),
            if (_error != null) Padding(
              padding: const EdgeInsets.symmetric(vertical: 8),
              child: Text(_error!, style: const TextStyle(color: Colors.red)),
            ),
            if (_resultado != null) Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Deficiencia: ${_resultado!.deficiencia}',
                      style: Theme.of(context).textTheme.titleLarge,
                    ),
                    const SizedBox(height: 4),
                    Text('Confianza: ${(_resultado!.confianza * 100).toStringAsFixed(1)}%'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                ElevatedButton.icon(
                  onPressed: () => _seleccionarImagen(ImageSource.camera),
                  icon: const Icon(Icons.camera_alt),
                  label: const Text('Cámara'),
                ),
                ElevatedButton.icon(
                  onPressed: () => _seleccionarImagen(ImageSource.gallery),
                  icon: const Icon(Icons.photo_library),
                  label: const Text('Galería'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}