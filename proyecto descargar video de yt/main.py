import flet as ft
from pytubefix import YouTube

def main(page: ft.Page):
    # --- 1. CONFIGURACIÓN DE LA APP (DISEÑO) ---
    page.title = "Descargador Simple"
    page.theme_mode = ft.ThemeMode.DARK
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    
    # Configuración para simular tamaño móvil en PC, 
    # en un celular real esto se adaptará automáticamente.
    page.window_width = 400 
    page.window_height = 700
    
    # Habilitamos scroll por si el teclado del celular tapa los controles
    page.scroll = ft.ScrollMode.AUTO 

    # ### NUEVO: CONFIGURACIÓN DEL FILEPICKER ###
    # Esta función se ejecuta cuando el usuario ya eligió la carpeta
    def al_seleccionar_carpeta(e: ft.FilePickerResultEvent):
        if e.path:
            # Si eligió una carpeta, iniciamos la descarga pasando esa ruta
            procesar_descarga(path_destino=e.path)
        else:
            # Si canceló, no hacemos nada
            entrada_url.error_text = "⚠️ Debes elegir una carpeta"
            page.update()

    # Creamos el componente y lo agregamos a la página oculta (overlay)
    file_picker = ft.FilePicker(on_result=al_seleccionar_carpeta)
    page.overlay.append(file_picker)
    page.add(file_picker)
    # ###########################################

    # ### NUEVO: FUNCIÓN INTERMEDIA ###
    # Esta función valida el link ANTES de abrir el selector de carpeta
    def abrir_selector(e):
        url_video = entrada_url.value
        if not url_video:
            entrada_url.error_text = "⚠️ Pega un enlace primero"
            page.update()
        else:
            entrada_url.error_text = None
            page.update()
            # Si hay link, abrimos el selector de carpeta
            file_picker.get_directory_path()
    # #################################

    # --- 2. LÓGICA DEL PROGRAMA (FUNCIONES) ---
    
    # MODIFICADO: Ahora acepta un argumento opcional "path_destino"
    def procesar_descarga(path_destino=None): 
        """
        Esta función contiene toda la lógica:
        1. Valida la URL.
        2. Conecta con YouTube.
        3. Busca la mejor calidad mixta (Audio+Video).
        4. Descarga el archivo.
        """
        url_video = entrada_url.value
        
        # Validación: ¿El campo está vacío?
        # (Esta validación ya se hace en abrir_selector, pero se deja por seguridad)
        if not url_video:
            entrada_url.error_text = "⚠️ Pega un enlace primero"
            page.update()
            return
        
        # Limpiamos errores previos y cambiamos estado visual
        entrada_url.error_text = None
        btn_accion.disabled = True
        btn_accion.text = "Conectando..."
        icono_estado.name = "downloading"
        icono_estado.color = "blue"
        texto_estado.value = "Iniciando conexión..."
        texto_estado.visible = True
        barra_progreso.visible = True
        page.update()

        try:
            # Paso A: Crear objeto YouTube
            yt = YouTube(url_video)
            
            # Actualizamos estado con el título del video
            texto_estado.value = f"Bajando: {yt.title[:20]}..."
            page.update()
            
            # Paso B: Obtener la mejor resolución PROGRESIVA
            # 'get_highest_resolution' busca el video con mayor calidad
            # que contenga AUDIO y VIDEO en el mismo archivo.
            # NOTA: Esto suele llegar máximo a 720p, pero asegura que se escuche.
            stream = yt.streams.get_highest_resolution()
            
            # Paso C: Descargar
            # ### MODIFICADO: Usamos la ruta del FilePicker ###
            if path_destino:
                stream.download(output_path=path_destino)
            else:
                stream.download() # Respaldo por si acaso
            # ###############################################

            # Éxito
            icono_estado.name = "check_circle"
            icono_estado.color = "green"
            texto_estado.value = "¡Video guardado!"
            entrada_url.value = "" # Limpiar campo

        except Exception as error:
            # Manejo de errores (Internet, Link inválido, etc)
            icono_estado.name = "error"
            icono_estado.color = "red"
            texto_estado.value = "Ocurrió un error"
            print(f"Error detallado: {error}") # Para ver en consola

        # Restaurar estado del botón
        btn_accion.disabled = False
        btn_accion.text = "Descargar Otro"
        barra_progreso.visible = False
        page.update()

    # --- 3. ELEMENTOS DE LA INTERFAZ (UI) ---
    
    # Título elegante
    lbl_titulo = ft.Text(
        "YouTube Downloader", 
        size=28, 
        weight=ft.FontWeight.BOLD,
        text_align=ft.TextAlign.CENTER
    )
    
    lbl_subtitulo = ft.Text(
        "Rápido y Simple", 
        color="grey",
        size=14
    )

    # Campo de texto optimizado para móviles
    # ### MODIFICADO: on_submit ahora llama al selector ###
    entrada_url = ft.TextField(
        label="Enlace del video",
        hint_text="https://youtube.com/...",
        prefix_icon="link",
        bgcolor="#303030",
        border_radius=15,
        keyboard_type=ft.KeyboardType.URL, # Abre teclado de URL en móvil
        on_submit=abrir_selector 
    )

    # Botón grande y fácil de tocar
    # ### MODIFICADO: on_click ahora llama al selector ###
    btn_accion = ft.ElevatedButton(
        text="DESCARGAR AHORA",
        icon="download",
        style=ft.ButtonStyle(
            padding=20,
            shape=ft.RoundedRectangleBorder(radius=12),
            bgcolor="blue",
            color="white",
        ),
        on_click=abrir_selector, 
        width=300 # Ancho fijo para que se vea bien
    )

    # Elementos de retroalimentación (Feedback)
    icono_estado = ft.Icon(name="cloud_download", size=60, color="blue")
    barra_progreso = ft.ProgressBar(width=200, color="orange", visible=False)
    texto_estado = ft.Text("", visible=False, size=16, weight=ft.FontWeight.W_500)

    # --- 4. ARMADO DE LA PÁGINA ---
    
    # Usamos un Container para darle fondo y bordes redondeados (estilo tarjeta)
    tarjeta_principal = ft.Container(
        content=ft.Column(
            controls=[
                icono_estado,
                lbl_titulo,
                lbl_subtitulo,
                ft.Divider(height=30, color="transparent"),
                entrada_url,
                ft.Divider(height=20, color="transparent"),
                btn_accion,
                ft.Divider(height=20, color="transparent"),
                barra_progreso,
                texto_estado
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=5
        ),
        padding=30,
        bgcolor="#252525",
        border_radius=25,
        width=350, # Ancho ideal para verse bien en cualquier cel
        shadow=ft.BoxShadow(blur_radius=20, color="black")
    )

    # Agregamos la tarjeta a la página
    page.add(tarjeta_principal)

# Ejecución
ft.app(target=main)