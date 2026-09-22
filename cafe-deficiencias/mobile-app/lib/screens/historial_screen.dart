import 'package:flutter/material.dart';
import '../models/registro_historial.dart';
import '../services/api_service.dart';

class HistorialScreen extends StatefulWidget {
  const HistorialScreen({super.key});

  @override
  State<HistorialScreen> createState() => _HistorialScreenState();
}

class _HistorialScreenState extends State<HistorialScreen> {
  final ApiService _apiService = ApiService();
  late Future<List<RegistroHistorial>> _futuroHistorial;

  @override
  void initState() {
    super.initState();
    _futuroHistorial = _apiService.obtenerHistorial();
  }

  Future<void> _recargar() async {
    setState(() {
      _futuroHistorial = _apiService.obtenerHistorial();
    });
    await _futuroHistorial;
  }

  Color _colorPorDeficiencia(String deficiencia) {
    switch (deficiencia) {
      case 'sana':
        return Colors.green;
      case 'nitrogeno':
        return Colors.orange;
      case 'potasio':
        return Colors.red;
      case 'magnesio':
        return Colors.purple;
      default:
        return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Historial de diagnósticos')),
      body: RefreshIndicator(
        onRefresh: _recargar,
        child: FutureBuilder<List<RegistroHistorial>>(
          future: _futuroHistorial,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }

            if (snapshot.hasError) {
              return ListView(
                children: [
                  const SizedBox(height: 100),
                  Center(
                    child: Text(
                      'No se pudo cargar el historial.\n¿Está corriendo el backend?',
                      textAlign: TextAlign.center,
                      style: const TextStyle(color: Colors.red),
                    ),
                  ),
                ],
              );
            }

            final registros = snapshot.data ?? [];

            if (registros.isEmpty) {
              return ListView(
                children: const [
                  SizedBox(height: 100),
                  Center(child: Text('Todavía no hay diagnósticos guardados.')),
                ],
              );
            }

            // Los más recientes primero
            registros.sort((a, b) => b.fecha.compareTo(a.fecha));

            return ListView.builder(
              itemCount: registros.length,
              itemBuilder: (context, index) {
                final registro = registros[index];
                return ListTile(
                  leading: CircleAvatar(
                    backgroundColor: _colorPorDeficiencia(registro.deficienciaDetectada),
                    child: Text(
                      '${(registro.confianza * 100).round()}%',
                      style: const TextStyle(fontSize: 10, color: Colors.white),
                    ),
                  ),
                  title: Text(registro.deficienciaDetectada),
                  subtitle: Text(
                    '${registro.fecha.day}/${registro.fecha.month}/${registro.fecha.year} '
                    '${registro.fecha.hour.toString().padLeft(2, '0')}:${registro.fecha.minute.toString().padLeft(2, '0')}'
                    '${registro.ubicacion != null ? ' · ${registro.ubicacion}' : ''}',
                  ),
                );
              },
            );
          },
        ),
      ),
    );
  }
}