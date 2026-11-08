import flet as ft
from pytubefix import YouTube

def main(page: ft.Page):
    # --- Configuración de la Ventana ---
    page.title = "YouTube Downloader Pro"
    page.theme_mode = ft.ThemeMode.DARK
    page.window_width = 500
    page.window_height = 650
    page.padding = 20
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # Variable para guardar el video cargado
    current_yt_object = None

    # --- Función para buscar y llenar opciones ---
    def buscar_calidades(e):
        nonlocal current_yt_object
        url = entrada_url.value
        
        if not url:
            entrada_url.error_text = "Ingresa una URL primero"
            page.update()
            return

        entrada_url.error_text = None
        btn_buscar.disabled = True
        btn_buscar.text = "Buscando..."
        page.update()

        try:
            yt = YouTube(url)
            current_yt_object = yt # Guardamos el objeto para usarlo luego
            
            # Limpiamos las opciones anteriores
            selector_calidad.options.clear()
            
            # 1. Buscamos opciones CON AUDIO (Progresivas - Max 720p)
            streams_con_audio = yt.streams.filter(progressive=True).order_by('resolution').desc()
            for s in streams_con_audio:
                if s.resolution:
                    selector_calidad.options.append(
                        ft.dropdown.Option(
                            text=f"[AUDIO+VIDEO] {s.resolution} (Completo)",
                            key=str(s.itag) # Usamos el 'itag' que es el ID único
                        )
                    )

            # 2. Buscamos opciones de ALTA CALIDAD (Adaptativas - Solo Video 1080p+)
            streams_alta = yt.streams.filter(adaptive=True, file_extension='mp4', only_video=True).order_by('resolution').desc()
            for s in streams_alta:
                # Filtramos para no repetir las bajas que ya pusimos arriba
                res_num = int(s.resolution.replace("p", "")) if s.resolution else 0
                if res_num >= 1080: 
                    selector_calidad.options.append(
                        ft.dropdown.Option(
                            text=f"[SOLO VIDEO] {s.resolution} (Alta Calidad - Sin Audio)",
                            key=str(s.itag)
                        )
                    )

            # Si no encontró nada
            if not selector_calidad.options:
                selector_calidad.options.append(ft.dropdown.Option("No se encontraron formatos mp4"))

            # Habilitar el segundo paso
            selector_calidad.disabled = False
            btn_descargar.disabled = False
            texto_estado.value = f"Video encontrado: {yt.title[:30]}..."
            texto_estado.color = "cyan"
            selector_calidad.value = selector_calidad.options[0].key # Seleccionar el primero por defecto

        except Exception as ex:
            texto_estado.value = f"Error al buscar: {str(ex)}"
            texto_estado.color = "red"
            print(ex)
        
        btn_buscar.disabled = False
        btn_buscar.text = "Buscar Calidades"
        page.update()

    # --- Función de Descarga ---
    def descargar_video(e):
        if not current_yt_object or not selector_calidad.value:
            return

        btn_descargar.disabled = True
        btn_descargar.text = "Descargando..."
        anillo_progreso.visible = True
        texto_estado.value = "Descargando video..."
        texto_estado.color = "blue"
        page.update()

        try:
            # Obtenemos el stream exacto usando el ID (itag)
            itag_seleccionado = int(selector_calidad.value)
            stream = current_yt_object.streams.get_by_itag(itag_seleccionado)
            
            stream.download()
            
            texto_estado.value = "✅ ¡Descarga completada!"
            texto_estado.color = "green"
            
        except Exception as ex:
            texto_estado.value = f"Error en descarga: {str(ex)}"
            texto_estado.color = "red"

        btn_descargar.disabled = False
        btn_descargar.text = "Descargar Selección"
        anillo_progreso.visible = False
        page.update()

    # --- Interfaz Gráfica ---
    titulo = ft.Text("Descargador Inteligente", size=24, weight=ft.FontWeight.BOLD)
    
    entrada_url = ft.TextField(
        label="Pegar Link de YouTube",
        prefix_icon="link",
        width=400,
        bgcolor="#303030",
        border_radius=10
    )

    btn_buscar = ft.ElevatedButton(
        text="1. Seleccionar calidad",
        icon="search",
        on_click=buscar_calidades,
        bgcolor="orange",
        color="white",
        width=200
    )

    selector_calidad = ft.Dropdown(
        width=400,
        label="Selecciona la Versión",
        hint_text="Primero busca el video...",
        disabled=True, # Deshabilitado hasta buscar
        bgcolor="#303030",
        border_radius=10
    )

    btn_descargar = ft.ElevatedButton(
        text="2. Descargar Selección",
        icon="download",
        on_click=descargar_video,
        disabled=True, # Deshabilitado hasta buscar
        bgcolor="green",
        color="white",
        width=200
    )

    texto_estado = ft.Text("Esperando URL...", color="grey")
    anillo_progreso = ft.ProgressRing(visible=False, width=20, height=20, color="green")

    # Contenedor
    tarjeta = ft.Container(
        content=ft.Column([
            ft.Icon("video_library", size=40, color="red"),
            titulo,
            ft.Divider(height=10, color="transparent"),
            entrada_url,
            btn_buscar,
            ft.Divider(height=10, color="transparent"),
            selector_calidad,
            btn_descargar,
            ft.Divider(height=10, color="transparent"),
            ft.Row([anillo_progreso, texto_estado], alignment=ft.MainAxisAlignment.CENTER)
        ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
        padding=30,
        bgcolor="#252525",
        border_radius=20,
        shadow=ft.BoxShadow(blur_radius=15, color="black")
    )

    page.add(tarjeta)

ft.app(target=main)