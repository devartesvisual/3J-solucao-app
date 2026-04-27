import flet as ft
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import ssl
import urllib.request

# Correção para o erro de Certificado SSL do Python no Windows
ssl._create_default_https_context = ssl._create_unverified_context

def main(page: ft.Page):
    page.title = "Gerador de Orçamentos - CODY sistemas"
    page.window.width = 500
    page.window.height = 750
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 30
    
    # Título
    title = ft.Text("3J SOLUÇÃO EM COMUNICAÇÃO VISUAL", size=24, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE_400)
    subtitle = ft.Text("Orçamentos", size=18, color=ft.Colors.GREY_400)

    # Campos de Entrada
    cliente_input = ft.TextField(label="Nome do Cliente", prefix_icon=ft.Icons.PERSON)
    descricao_input = ft.TextField(label="Descrição do Trabalho", multiline=True, min_lines=3, prefix_icon=ft.Icons.DESCRIPTION)
    
    largura_input = ft.TextField(label="Largura (m)", prefix_icon=ft.Icons.SWAP_HORIZ, expand=1)
    altura_input = ft.TextField(label="Altura (m)", prefix_icon=ft.Icons.SWAP_VERT, expand=1)
    valor_input = ft.TextField(label="Valor em m² (R$)", prefix_icon=ft.Icons.MONETIZATION_ON, expand=1)

    # Valor Total Live
    total_text = ft.Text("R$ 0,00", size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.GREEN_400)

    # Lógica de cálculo dinâmico
    def calcular_total(e):
        try:
            l = float(largura_input.value.replace(",", ".")) if largura_input.value else 0.0
            a = float(altura_input.value.replace(",", ".")) if altura_input.value else 0.0
            v = float(valor_input.value.replace(",", ".")) if valor_input.value else 0.0
            total = l * a * v
            
            # Formatando para moeda BR
            total_formatado = f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            total_text.value = total_formatado
        except ValueError:
            total_text.value = "R$ 0,00"
        
        page.update()

    # Adicionar eventos on_change
    largura_input.on_change = calcular_total
    altura_input.on_change = calcular_total
    valor_input.on_change = calcular_total

    # File Picker para Salvar o PDF
    file_picker = ft.FilePicker()

    async def iniciar_geracao_pdf(e):
        if not cliente_input.value or not descricao_input.value or not largura_input.value or not altura_input.value or not valor_input.value:
            snack = ft.SnackBar(ft.Text("Preencha todos os campos!"), bgcolor=ft.Colors.RED_500)
            page.overlay.append(snack)
            snack.open = True
            page.update()
            return
            
        caminho_arquivo = await file_picker.save_file(
            dialog_title="Salvar Orçamento PDF",
            file_name=f"Orcamento_{cliente_input.value.replace(' ', '_')}.pdf",
            allowed_extensions=["pdf"]
        )
        
        if caminho_arquivo:
            gerar_pdf_action(caminho_arquivo)

    def gerar_pdf_action(caminho_arquivo):
        try:
            cliente = cliente_input.value.strip()
            descricao = descricao_input.value.strip()
            largura = float(largura_input.value.replace(",", "."))
            altura = float(altura_input.value.replace(",", "."))
            valor_m2 = float(valor_input.value.replace(",", "."))
            valor_total = largura * altura * valor_m2

            c = canvas.Canvas(caminho_arquivo, pagesize=A4)
            width, height = A4
            
            c.setFont("Helvetica-Bold", 18)
            c.drawCentredString(width / 2.0, height - 60, "ORÇAMENTO")
            c.setLineWidth(1)
            c.line(50, height - 75, width - 50, height - 75)
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, height - 110, "Cliente:")
            c.setFont("Helvetica", 12)
            c.drawString(110, height - 110, cliente)
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, height - 140, "Medidas:")
            c.setFont("Helvetica", 12)
            medidas_texto = f"{largura:.2f} m (Largura)  x  {altura:.2f} m (Altura)"
            c.drawString(115, height - 140, medidas_texto)
            
            c.setFont("Helvetica-Bold", 12)
            c.drawString(50, height - 170, "Descrição do Trabalho:")
            c.setFont("Helvetica", 12)
            
            y_text = height - 190
            for linha in descricao.split('\n'):
                if y_text < 100:
                    c.showPage()
                    c.setFont("Helvetica", 12)
                    y_text = height - 50
                c.drawString(50, y_text, linha)
                y_text -= 18
            
            c.line(50, y_text - 10, width - 50, y_text - 10)
            
            y_valor = y_text - 40
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y_valor, "Valor Total:")
            valor_formatado = f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            c.drawString(140, y_valor, valor_formatado)
            
            c.setFont("Helvetica-Oblique", 10)
            c.drawCentredString(width / 2.0, 50, "Orçamento válido por 15 dias úteis.")
            c.drawCentredString(width / 2.0, 35, "3J SOLUÇÃO EM COMUNICAÇÃO VISUAL.")

            c.save()

            snack_success = ft.SnackBar(ft.Text("PDF gerado com sucesso!"), bgcolor=ft.Colors.GREEN_600)
            page.overlay.append(snack_success)
            snack_success.open = True
            page.update()

        except Exception as e:
            snack_error = ft.SnackBar(ft.Text(f"Erro: {str(e)}"), bgcolor=ft.Colors.RED_500)
            page.overlay.append(snack_error)
            snack_error.open = True
            page.update()

    btn_exportar = ft.ElevatedButton(
        "Gerar PDF do Orçamento", 
        icon=ft.Icons.PICTURE_AS_PDF, 
        on_click=iniciar_geracao_pdf,
        style=ft.ButtonStyle(
            bgcolor=ft.Colors.BLUE_800,
            color=ft.Colors.WHITE,
            padding=20,
        ),
        width=400
    )

    page.add(
        ft.Column([
            title,
            subtitle,
            ft.Divider(height=20, color="transparent"),
            cliente_input,
            descricao_input,
            ft.Row([largura_input, altura_input]),
            valor_input,
            ft.Divider(height=10, color="transparent"),
            ft.Container(
                content=ft.Column([
                    ft.Text("VALOR FINAL", size=12, color=ft.Colors.GREY_400),
                    total_text,
                ], horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                alignment=ft.Alignment(0, 0),
                padding=20,
                bgcolor=ft.Colors.SURFACE_CONTAINER,
                border_radius=10,
            ),
            ft.Divider(height=10, color="transparent"),
            ft.Row([btn_exportar], alignment=ft.MainAxisAlignment.CENTER)
        ], scroll=ft.ScrollMode.AUTO, expand=True)
    )

if __name__ == "__main__":
    ft.run(main)
