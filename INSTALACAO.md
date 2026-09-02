# Instalação multiplataforma

## Windows 10/11

1. Instale Python 3.11 ou superior pelo python.org e marque **Add Python to PATH**.
2. Extraia o ZIP para uma pasta permanente.
3. Execute `install_windows.bat`.
4. Depois, abra `iniciar_windows.bat`.

Para gerar um único `.exe`, execute `build_windows.bat`. O arquivo será criado em `dist`.

O SAT físico normalmente funciona somente no Windows, pois depende da DLL do fabricante. Python e DLL precisam ter a mesma arquitetura, frequentemente x86/32 bits.

## Linux

Instale Python, venv e bibliotecas gráficas. Em Ubuntu/Debian:

```bash
sudo apt install python3 python3-venv libegl1 libgl1 libxcb-cursor0
chmod +x instalar_linux.sh
./instalar_linux.sh
./iniciar_linux.sh
```

Para gerar o binário Linux: `./build_linux.sh`.

## macOS

1. Instale Python 3.11+ pelo python.org.
2. Clique com o botão direito em `instalar_macos.command` e escolha **Abrir**.
3. Depois, abra `iniciar_macos.command`.

Se o macOS bloquear o script, use **Ajustes do Sistema → Privacidade e Segurança → Abrir Mesmo Assim**. Para gerar um `.app`, execute `build_macos.command`.

## Observação sobre executáveis

PyInstaller não faz compilação cruzada: `.exe`, binário Linux e `.app` devem ser gerados em Windows, Linux e macOS, respectivamente. Os scripts incluídos automatizam essa geração. Certificados de assinatura de código e notarização Apple não estão incluídos.
