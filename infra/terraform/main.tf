terraform {
  required_version = ">= 1.5.0"
  required_providers {
    local = {
      source  = "hashicorp/local"
      version = "~> 2.4"
    }
  }
}

provider "local" {}

# This Terraform configuration is a scaffold only. It demonstrates how to lay
# out resources for a safe, isolated ADCS lab. Replace the "local_file" blocks
# with modules/resources for your hypervisor or cloud that **never** connect to
# production.

variable "lab_name" {
  description = "Name prefix for the lab resources"
  type        = string
  default     = "adcs-lab"
}

variable "vm_count" {
  description = "Number of generic Windows member servers"
  type        = number
  default     = 2
}

resource "local_file" "dc" {
  content  = "Domain Controller placeholder for ${var.lab_name}"
  filename = "${path.module}/artifacts/dc.txt"
}

resource "local_file" "root_ca" {
  content  = "Enterprise Root CA placeholder for ${var.lab_name}"
  filename = "${path.module}/artifacts/root-ca.txt"
}

resource "local_file" "sub_ca" {
  content  = "Subordinate CA placeholder for ${var.lab_name}"
  filename = "${path.module}/artifacts/sub-ca.txt"
}

resource "local_file" "web_enrollment" {
  content  = "Web Enrollment placeholder for ${var.lab_name}"
  filename = "${path.module}/artifacts/web-enrollment.txt"
}

resource "local_file" "workstations" {
  count    = var.vm_count
  content  = "Workstation ${count.index} placeholder"
  filename = "${path.module}/artifacts/workstation-${count.index}.txt"
}

output "lab_artifacts" {
  value = [
    local_file.dc.filename,
    local_file.root_ca.filename,
    local_file.sub_ca.filename,
    local_file.web_enrollment.filename,
  ]
  description = "Paths to generated placeholders; swap with real VM IDs in your environment."
}
