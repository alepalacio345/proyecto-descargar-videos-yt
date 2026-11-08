from pytubefix import YouTube

def main():
    # 1. Pedimos el link directamente en la consola
    url = input("Pegar enlace de YouTube aquí: ")

    try:
        print("Conectando con YouTube...")
        yt = YouTube(url)

        print(f"Título: {yt.title}")
        print("Buscando la máxima calidad de video disponible (1080p, 4K, etc)...")

        # 2. FILTRO DE ALTA CALIDAD
        # - adaptive=True: Busca streams que YouTube usa para 1080p/4K (separados del audio).
        # - only_video=True: Ignora si tiene audio o no (normalmente no tienen en alta calidad).
        # - order_by('resolution'): Ordena del peor al mejor.
        # - desc(): Invierte la lista (el mejor queda de primero).
        # - first(): Agarra el primero (el ganador).
        stream = yt.streams.filter(
            adaptive=True, 
            file_extension='mp4', 
            only_video=True
        ).order_by('resolution').desc().first()

        # Mostramos qué calidad encontró
        print(f"Calidad encontrada: {stream.resolution} - {stream.mime_type}")
        
        # 3. Descarga
        print("Descargando... (esto puede tardar si es 4K)")
        stream.download()
        
        print("✅ ¡Descarga completada con éxito!")

    except Exception as e:
        print(f"❌ Ocurrió un error: {e}")

# Ejecutamos la función principal
if __name__ == "__main__":
    main()