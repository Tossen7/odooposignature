if record.state == 'purchase':
    creator = record.create_uid
    creator_name = creator.name if creator else False

    creator_signature = False
    if creator and creator.sign_signature:
        # signature is already base64 in Odoo, just ensure it's a string
        if isinstance(creator.sign_signature, bytes):
            creator_signature = creator.sign_signature.decode('utf-8')
        else:
            creator_signature = str(creator.sign_signature)

    # --- Approval details ---
    approver = record.write_uid
    approver_name = approver.name if approver else False

    approver_signature = False
    if approver and approver.sign_signature:
        if isinstance(approver.sign_signature, bytes):
            approver_signature = approver.sign_signature.decode('utf-8')
        else:
            approver_signature = str(approver.sign_signature)


    # --- Report data dictionary ---
    report_data = {
        'creator_signature': creator_signature,
        'creator_name': creator_name,
        'approver_name': approver_name,
        'approver_signature': approver_signature,
    }

    pdf_content, _ = env['ir.actions.report']._render_qweb_pdf(
        'purchase.action_report_purchase_order',
        res_ids=[record.id],
        data=report_data
    )

    pdf_base64 = b64encode(pdf_content).decode('ascii')

    attachment = env['ir.attachment'].create({
        'name': f'Purchase Order - {record.name}.pdf',
        'type': 'binary',
        'datas': pdf_base64,
        'res_model': 'purchase.order',
        'res_id': record.id,
        'mimetype': 'application/pdf',
    })

    record.message_post(
        body=f"PDF generated for Purchase Order {record.name}. "
             f"Created by: {creator_name}. "
             f"Approved by: {approver_name if approver_name else 'N/A'}",
        attachment_ids=[attachment.id],
        subtype_xmlid='mail.mt_note'
    )
