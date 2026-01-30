import subprocess


def compile_mjml(input_file: str, output_file: str):
    subprocess.run(["mjml", input_file, "-o", output_file], check=True)


compile_mjml("/home/pcnerd/projects/record_manipulator/backend/src/app/email_templates/src/otp_verification.mjml", "/home/pcnerd/projects/record_manipulator/backend/src/app/email_templates/build/otp_verification.html")
